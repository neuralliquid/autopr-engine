import pydantic
import asyncio
from autopr.actions.base import Action

class Inputs(pydantic.BaseModel):
    pass

class Outputs(pydantic.BaseModel):
    report: str
    exit_code: int

class RunDupCheck(Action[Inputs, Outputs]):
    """
    Runs the 'pnpm dup-check' command to check for code duplication.
    """
    id = "run_dup_check"

    async def run(self, inputs: Inputs) -> Outputs:
        command = "pnpm dup-check"
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        
        output = stdout.decode("utf-8") + stderr.decode("utf-8")
        
        return Outputs(
            report=output,
            exit_code=process.returncode
        )

if __name__ == "__main__":
    from autopr.tests.utils import run_action_manually
    asyncio.run(
        run_action_manually(
            action=RunDupCheck,
            inputs=Inputs(),
        )
    ) 