# cli.py
import asyncio
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from src.dispatcher import Dispatcher

console = Console()


def print_route_info(route: str):
    colors = {"faq": "blue", "complaint": "red", "agent": "yellow"}
    labels = {"faq": "📖 FAQ 問答", "complaint": "⚠️ 客訴處理", "agent": "👤 轉接人工"}
    color = colors.get(route, "white")
    label = labels.get(route, route)
    console.print(Panel(f"[bold {color}]{label}[/]", expand=False))


async def main():
    console.print("[bold cyan]🛒 電商客服 AI Agent[/]")
    console.print("[dim]輸入問題 / 客訴，輸入 'quit' 離開[/]\n")

    dispatcher = Dispatcher()

    while True:
        text = console.input("[bold green]顧客:[/] ")
        if text.lower() in ("quit", "exit", "q"):
            break

        with console.status("[bold yellow]AI 思考中..."):
            result = await dispatcher.handle(text)

        print_route_info(result["route"])

        if result["route"] == "faq":
            console.print(Markdown(f"\n**AI:** {result['response']}"))
        elif result["route"] == "complaint":
            if result.get("type") == "escalate":
                console.print(f"[bold red]⚠️ 已升級人工客服[/]")
                console.print(f"[red]案件編號: {result.get('case_id', 'N/A')}[/]")
                console.print(f"[red]原因: {result.get('reason', '')}[/]")
            else:
                console.print(Markdown(f"\n**AI回覆:** {result.get('response', '')}"))
                if result.get("case_id"):
                    console.print(f"[dim]案件編號: {result['case_id']}[/]")
        else:  # agent
            console.print(f"[yellow]{result.get('response', '')}[/]")

        console.print()


if __name__ == "__main__":
    asyncio.run(main())
