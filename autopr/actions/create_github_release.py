import pydantic
from autopr.actions.base import Action

class Inputs(pydantic.BaseModel):
    tag_name: str
    name: str
    body: str
    is_draft: bool = True
    is_prerelease: bool = False

class Outputs(pydantic.BaseModel):
    success: bool
    release_url: str

class CreateGithubRelease(Action[Inputs, Outputs]):
    """
    [Simulation] Creates a new draft release in GitHub.
    """
    id = "create_github_release"

    async def run(self, inputs: Inputs) -> Outputs:
        print("--- Create GitHub Release ---")
        print(f"Tag: {inputs.tag_name}")
        print(f"Name: {inputs.name}")
        print(f"Draft: {inputs.is_draft}")
        print(f"Prerelease: {inputs.is_prerelease}")
        print(f"Body:\\n{inputs.body}")
        
        simulated_url = f"https://github.com/example/repo/releases/tag/{inputs.tag_name}"
        
        return Outputs(
            success=True,
            release_url=simulated_url
        )

if __name__ == "__main__":
    from autopr.tests.utils import run_action_manually
    import asyncio
    asyncio.run(
        run_action_manually(
            action=CreateGithubRelease,
            inputs=Inputs(
                tag_name="v1.0.0",
                name="Version 1.0.0",
                body="Initial release."
            ),
        )
    ) 