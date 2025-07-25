import pydantic
from autopr.actions.base import Action
from typing import List, Dict, Any


class Inputs(pydantic.BaseModel):
    days_stale: int = 30
    type: str = "issue"  # or "pr"


class Outputs(pydantic.BaseModel):
    stale_items: List[Dict[str, Any]] = pydantic.Field(default_factory=list)
    report: str = ""


class FindStaleIssuesOrPRs(Action[Inputs, Outputs]):
    """
    [Simulation] Finds stale issues or PRs with no activity for a given number of days.
    """

    id = "find_stale_issues_or_prs"

    async def run(self, inputs: Inputs) -> Outputs:
        print(
            f"--- Finding stale {inputs.type}s older than {inputs.days_stale} days ---"
        )
        # In a real implementation, you would use the GitHub API
        # For simulation, return a fake list
        stale = [
            {
                "number": 101,
                "title": "Old Issue",
                "url": "https://github.com/example/repo/issues/101",
            },
            {
                "number": 202,
                "title": "Stale PR",
                "url": "https://github.com/example/repo/pull/202",
            },
        ]
        report = f"Found {len(stale)} stale {inputs.type}s."
        return Outputs(stale_items=stale, report=report)


if __name__ == "__main__":
    from autopr.tests.utils import run_action_manually
    import asyncio

    asyncio.run(
        run_action_manually(
            action=FindStaleIssuesOrPRs,
            inputs=Inputs(),
        )
    )
