# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -*- coding: utf-8 -*-

import logging
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

from langchain_community.document_loaders import PyPDFLoader  # to load and parse PDFs
import markdown  # to format LLM output for web display

import os  # to remove temp PDF files
import uuid  # to generate temporary PDF filenames

from flask import Flask, render_template, redirect, url_for, session
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, CSRFProtect
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields import SubmitField, TextAreaField

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = "dev"

# set default button sytle and size, will be overwritten by macro parameters
app.config["BOOTSTRAP_BTN_STYLE"] = "primary"
app.config["BOOTSTRAP_BTN_SIZE"] = "sm"

bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)


class UploadForm(FlaskForm):
    """A basic form to upload a file and take a text prompt."""

    pdf_file = FileField(
        validators=[
            FileRequired(),
            FileAllowed(["pdf"], "Please select a PDF."),
        ],
        label="Select a PDF",
    )
    text_input = TextAreaField(label="Instructions", default="Summarize the PDF.")
    submit = SubmitField()


vertexai.init(project=os.environ["PROJECT_ID"], location="us-central1")

model = GenerativeModel("gemini-pro")

generation_config = GenerationConfig(
    temperature=0.3,
    top_p=0.6,
    candidate_count=1,
    max_output_tokens=4096,
)


@app.route("/", methods=["GET", "POST"])
def index():
    """Route to display the input form and query the LLM."""
    form = UploadForm()
    if form.validate_on_submit():
        pdf_temp_filename = str(uuid.uuid4())
        form.pdf_file.data.save(pdf_temp_filename)
        loader = PyPDFLoader(pdf_temp_filename)
        pages = loader.load_and_split()
        combined_text = "\n\n".join([p.page_content for p in pages])
        word_count = len(combined_text.split())
        logging.debug(f"pages: {len(pages)}")
        logging.debug(f"word_count combined: {word_count}")
        # 18500 words times ~1.66 tokens per words should keep us under Gemini's token limit:
        # https://ai.google.dev/models/gemini#model-variations
        if word_count < 18500:
            prompt = f"{form.text_input.data} Use information from the PDF to respond.\n\nPDF:\n{combined_text}"
            logging.debug(prompt)
            response = model.generate_content(
                prompt, generation_config=generation_config
            )
            response_text = response.text.replace("•", "  *")
        else:
            response_text = "This text is too long for this application's current configuration.\n\nPlease use a shorter text."
        markdown_response = markdown.markdown(response_text)
        session["markdown_response"] = markdown_response
        logging.debug(f"Response: \n{markdown_response}")
        os.remove(pdf_temp_filename)
        return redirect(url_for("pdf_results"))

    return render_template("index.html", upload_form=form)


@app.route("/pdf_results", methods=["GET", "POST"])
def pdf_results():
    """Route to display results."""

    # flash("Awaiting the model's response!")

    return render_template(
        "pdf_results.html", response_text=session["markdown_response"]
    )


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
