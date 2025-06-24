import gradio as gr
from model import pokemon_search

custom_theme = gr.themes.Monochrome(
    primary_hue="pink"
)

demo = gr.Interface(
    fn=pokemon_search,
    inputs=gr.Textbox(label="포켓몬을 묘사해보세요!", placeholder="예: 보라색 풍선, 솜사탕, 분홍색..."),
    outputs=[
        gr.Gallery(label="Top 5 포켓몬 이미지", columns=5, height="auto"),
        gr.Textbox(label="포켓몬 이름 + 점수", lines=7),
        gr.Textbox(label="포켓몬 설명", lines=7),
    ],
    title="포켓몬 외형 설명 기반 검색기",
    description="포켓몬의 외형/특징을 한국어로 입력하면, 가장 비슷한 포켓몬 Top 5를 이미지와 함께 보여줍니다."
)

demo.launch(share=True)
