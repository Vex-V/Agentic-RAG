
import aiofiles

async def save_request_to_file(url: str, questions: List[str], filename="saving.txt"):
    async with aiofiles.open(filename, "a", encoding="utf-8") as f: