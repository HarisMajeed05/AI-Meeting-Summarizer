from django import forms


class MeetingForm(forms.Form):
    text_input = forms.CharField(
        label="Meeting Transcript (Text)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 8, "placeholder": "Paste full transcript here..."}),
    )
    audio_file = forms.FileField(
        label="Meeting Audio File",
        required=False,
        help_text="Upload an audio file (e.g., WAV, MP3)",
    )

    def clean(self):
        cleaned = super(MeetingForm, self).clean()
        text = cleaned.get("text_input") or ""
        audio = cleaned.get("audio_file")

        if not text.strip() and not audio:
            raise forms.ValidationError("Please provide either text or an audio file.")

        # Optional: simple size check for audio
        if audio and audio.size > 25 * 1024 * 1024:
            raise forms.ValidationError("Audio file is too large (max 25 MB).")

        return cleaned
