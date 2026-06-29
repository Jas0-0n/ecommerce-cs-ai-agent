# cli.py
import asyncio
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from src.dispatcher import Dispatcher

console = Console()


def print_route_info(route: str):
    colors = {"faq": "blue", "complaint": "red", "agent": "yellow"}
    labels = {"faq": "📖 FAQ", "complaint": "⚠️ Complaint", "agent": "👤 Human Transfer"}
    color = colors.get(route, "white")
    label = labels.get(route, route)
    console.print(Panel(f"[bold {color}]{label}[/]", expand=False))


async def main():
    console.print("[bold cyan]🛒 E-commerce CS AI Agent[/]")
    console.print("[dim]Enter your question / complaint, type 'quit' to exit[/]\n")

    dispatcher = Dispatcher()

    while True:
        text = console.input("[bold green]Customer:[/] ")
        if text.lower() in ("quit", "exit", "q"):
            break

        with console.status("[bold yellow]AI thinking..."):
            result = await dispatcher.handle(text)

        print_route_info(result["route"])

        if result["route"] == "faq":
            console.print(Markdown(f"\n**AI:** {result['response']}"))
        elif result["route"] == "complaint":
            if result.get("type") == "escalate":
                console.print(f"[bold red]⚠️ Escalated to human agent[/]")
                console.print(f"[red]Case ID: {result.get('case_id', 'N/A')}[/]")
                console.print(f"[red]Reason: {result.get('reason', '')}[/]")
            else:
                console.print(Markdown(f"\n**AI Reply:** {result.get('response', '')}"))
                if result.get("case_id"):
                    console.print(f"[dim]Case ID: {result['case_id']}[/]")
        else:  # agent
            console.print(f"[yellow]{result.get('response', '')}[/]")

        console.print()


if __name__ == "__main__":
    asyncio.run(main())
