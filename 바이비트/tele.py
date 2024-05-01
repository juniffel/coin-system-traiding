import telegram 
from telegram.constants import ParseMode

async def  tele_bot(message, reply=None): #실행시킬 함수명 임의지정
    """
    텔레그램 메세지 전송 
    message :  전송할 메세지 str
    """
    # token
    with open('/home/joon/바탕화면/coin/바이비트/알트토큰.txt') as f:
        lines = f.readlines()
        token = lines[0].strip()
        id = lines[1].strip()
        
    bot = telegram.Bot(token = token)
    await bot.send_message(chat_id=id, text=message, parse_mode = ParseMode.HTML, reply_markup = reply)



