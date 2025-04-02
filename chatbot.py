import random
import nltk
from nltk.chat.util import Chat, reflections
pares  = [
    [
        r"Oi | Ola | E ai",
        ["Olá, Como Posso Ajudar?", "Oi, como está?"],
    ],
    [
        r"Qua é o seu Nome?",
        ["Quem é John Galt"]
    ],
    [
        r"(.*)\?",
        ["Desculpe Não tenho uma resposta"]
    ]
    
]
pares.extend([
[r"(.*)", ["Como isso afeta o Gremio?","hummm é mesmo?"]],
])
reflexoes={
    "eu : você",
    "meu : seu",
    "você : eu",
    "seu : meu",
    "eu sou : você é",
    "você é : eu sou",
    "você estava : eu estava",
    "eu estava : voce estava"

}
chatbot = Chat(pares,reflections)
while True:
    user_input = input("Você: ")
    if user_input.lower() == "sair":
        print("ChatBot: Do the L 👆")
        break
    response = chatbot.respond(user_input)
    print("ChatBot", response)
