import asyncio
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from src.dispatcher import Dispatcher
from src.config import settings

console = Console()


def print_route_info(route: str):
    colors = {"faq": "blue", "complaint": "red", "agent": "yellow"}
    labels = {"faq": "📖 FAQ", "complaint": "⚠️ 投诉", "agent": "👤 转人工"}
    color = colors.get(route, "white")
    label = labels.get(route, route)
    console.print(Panel(f"[bold {color}]{label}[/]", expand=False))


async def main():
    console.print("[bold cyan]🛒 电商客服 AI Agent[/]")
    console.print("[dim]输入问题或投诉，输入 'quit' 退出[/]\n")

    dispatcher = Dispatcher()
    history: list[dict] = []  # conversation history

    while True:
        text = console.input("[bold green]客户:[/] ")
        if text.lower() in ("quit", "exit", "q"):
            break

        # Add to history
        history.append({"role": "user", "content": text})

        # Keep only recent N turns
        max_turns = settings.max_history_turns
        if len(history) > max_turns * 2:
            history = history[-(max_turns * 2):]

        with console.status("[bold yellow]AI思考中..."):
            route_info = await dispatcher.route(text)

        print_route_info(route_info["route"])

        if route_info["route"] == "faq":
            # Stream the response
            console.print("\n[bold]AI:[/] ", end="")
            full_response = ""
            async for chunk in dispatcher.faq_agent.answer_stream(text):
                if isinstance(chunk, str):
                    console.print(chunk, end="", highlight=False)
                    full_response += chunk
            console.print()  # newline
            history.append({"role": "assistant", "content": full_response})

        elif route_info["route"] == "complaint":
            result = await dispatcher.complain_agent.handle(text, route_info.get("sentiment"))
            if result.get("type") == "escalate":
                console.print("[bold red]⚠️ 已转接人工客服[/]")
                console.print(f"[red]工单编号: {result.get('case_id', 'N/A')}[/]")
                console.print(f"[red]原因: {result.get('reason', '')}[/]")
                history.append({"role": "assistant", "content": f"[转人工] 工单: {result.get('case_id', '')}"})
            else:
                response = result.get("response", "")
                console.print(Markdown(f"\n**AI回复:** {response}"))
                if result.get("case_id"):
                    console.print(f"[dim]工单编号: {result['case_id']}[/]")
                history.append({"role": "assistant", "content": response})

        else:  # agent
            msg = "正在为您转接人工客服，请稍候……"
            console.print(f"[yellow]{msg}[/]")
            history.append({"role": "assistant", "content": msg})

        console.print()


if __name__ == "__main__":
    asyncio.run(main())
