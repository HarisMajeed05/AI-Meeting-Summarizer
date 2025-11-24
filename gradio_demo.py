import gradio as gr

from core.application.orchestrator import (
    summarize_from_text,
    process_audio,
)


def summarize_text_interface(text: str):
    summary, actions, dates = summarize_from_text(text)
    date_rows = [[d["date"], d["context"]] for d in dates]
    return summary, actions, date_rows


def process_audio_interface(audio_path: str):
    transcript, summary, actions, dates = process_audio(audio_path)
    date_rows = [[d["date"], d["context"]] for d in dates]
    return transcript, summary, actions, date_rows


def build_demo():
    with gr.Blocks(title="Meeting Summarizer — Gradio Prototype") as demo:
        gr.Markdown(
            "### Meeting Summarizer (Gradio Prototype)\n"
            "Upload **audio** or paste **text** → summary, action items, and important dates."
        )

        with gr.Tab("From Text"):
            txt = gr.Textbox(
                label="Paste meeting text / transcript",
                lines=10,
                placeholder="Paste full text here...",
            )
            btn_t = gr.Button("Summarize")

            out_sum_t = gr.Textbox(label="Summary", lines=6)
            out_actions_t = gr.JSON(label="Action Items (JSON)")
            out_dates_t = gr.Dataframe(
                headers=["date", "context"], label="Important Dates", interactive=False
            )

            btn_t.click(
                summarize_text_interface,
                inputs=txt,
                outputs=[out_sum_t, out_actions_t, out_dates_t],
            )

        with gr.Tab("From Audio"):
            aud = gr.Audio(
                sources=["upload", "microphone"], type="filepath", label="Upload/Record audio"
            )
            btn_a = gr.Button("Transcribe + Summarize")

            out_tr = gr.Textbox(label="Transcript", lines=6)
            out_sum_a = gr.Textbox(label="Summary", lines=6)
            out_actions_a = gr.JSON(label="Action Items (JSON)")
            out_dates_a = gr.Dataframe(
                headers=["date", "context"], label="Important Dates", interactive=False
            )

            btn_a.click(
                process_audio_interface,
                inputs=aud,
                outputs=[out_tr, out_sum_a, out_actions_a, out_dates_a],
            )

    return demo


if __name__ == "__main__":
    demo = build_demo()
    demo.launch(share=False, debug=True)
