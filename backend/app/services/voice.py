import asyncio, edge_tts

async def _save(text, voice, output):
    await edge_tts.Communicate(text, voice).save(output)

def generate_voiceover(text, voice, output):
    asyncio.run(_save(text, voice, output))
