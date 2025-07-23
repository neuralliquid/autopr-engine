import pydantic
import asyncio
import os
from autopr.actions.base import Action

class Inputs(pydantic.BaseModel):
    database_connection_string: str
    seed_file_path: str

class Outputs(pydantic.BaseModel):
    success: bool
    log: str

class SeedDatabase(Action[Inputs, Outputs]):
    """
    Seeds a database with data from a specified SQL file.
    This is a simulation assuming a CLI tool like 'psql' is available.
    """
    id = "seed_database"

    async def run(self, inputs: Inputs) -> Outputs:
        if not os.path.isfile(inputs.seed_file_path):
            return Outputs(success=False, log=f"Error: Seed file '{inputs.seed_file_path}' not found.")

        # Simulating with a command: psql -d <conn_string> -f <file>
        command = f'echo "psql -d {inputs.database_connection_string} -f {inputs.seed_file_path}"'
        
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        log = f"--- Seeding with {inputs.seed_file_path} ---\n"
        log += stdout.decode('utf-8')
        log += stderr.decode('utf-8')
        
        success = process.returncode == 0
        if not success:
            log += f"--- FAILED ---"
        
        return Outputs(success=success, log=log)

if __name__ == "__main__":
    from autopr.tests.utils import run_action_manually
    # Create a dummy seed file for testing
    with open("seed-test.sql", "w") as f: f.write("INSERT INTO users VALUES (1, 'test');")
    asyncio.run(
        run_action_manually(
            action=SeedDatabase,
            inputs=Inputs(
                database_connection_string="dummy_connection_string",
                seed_file_path="seed-test.sql"
            ),
        )
    ) 