import edge_tts
import asyncio

async def generate_audio(text,outputFilename):
    communicate = edge_tts.Communicate(text,"en-AU-WilliamNeural")
    await communicate.save(outputFilename)
    return outputFilename


if __name__=="__main__":
    asyncio.run(generate_audio("Calling all saree lovers! Diwali is here, and we're celebrating with a dazzling sale. Get ready to light up your wardrobe with our exquisite collection of sarees, now at 50% off! From traditional silks to contemporary georgettes, we have a saree for every taste and occasion. Immerse yourself in the vibrant colors, intricate designs, and luxurious fabrics that define the timeless elegance of Indian sarees. Whether you're dressing up for a festive gathering or simply want to add a touch of glamour to your everyday style, our Diwali saree sale has something for you. Visit our store today and let the spirit of Diwali shine through your wardrobe!",
                               "audio.mp3"))