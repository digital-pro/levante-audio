# Levante Audio

Levente Audio is a graphical user interface for the ElevenLabs API. It can also utilize OpenAI's Whisper for speech-to-text transcription, if installed.
## Features

With Levante Audio, you can:

- Interact with the ElevenLabs API in real-time
- Record or upload audio files for transcription via OpenAI's Whisper (optional)
- Convert text to audio using ElevenLabs
- View and play back your ElevenLabs sample history

## Installation



Ensure you have Python 3.9 or higher installed. Creating a Python virtual environment before the installation is recommended.

To install the application, first clone the repository:

```bash
git clone https://github.com/digital-pro/levante-audio.git
```

Then navigate into the directory and install the package using pip:

```bash
cd levante-audio
pip install .

```
To use OpenAI's Whisper API or a local Whisper implementation for transcription, you can install the extras like this:

```bash
pip install .[whisper_api]
```
Or:

```bash
pip install .[whisper_local]
```
Or if you want both:

```bash
pip install .[whisper_api,whisper_local]
```
### For zsh users (default in macOS Catalina and later)

For zsh users, use quotation marks due to the way zsh handles square brackets:
```bash
pip install ".[whisper_api]"
```
```bash
pip install ".[whisper_local]"
```
Or if you want both:
```bash
pip install ".[whisper_api,whisper_local]"
```
### :construction: Important notes for Linux and macOS users :construction:
#### Tkinter Installation
**For Linux:** Make sure tkinter is installed for your Python environment. You can do this by installing the python3-tk package using your package manager. For example, if you're using Ubuntu, you can install it with:
```bash
sudo apt-get install python3-tk
```
**For macOS:** Install tkinter via Homebrew:
```bash
brew install python-tk@3.9
```
#### OpenSSL Issue (macOS only)
**If you encounter an error with urllib3:** You may need to install or update OpenSSL. Use Homebrew to install OpenSSL:
```bash
brew install openssl
```
If you've already installed OpenSSL but you're still encountering the error, reinstall Python linked with the Homebrew version of OpenSSL:

```bash
brew reinstall python
```
If the error persists, try installing an older version of `urllib3`:

```bash
pip3 install 'urllib3<2.0'
```

## Optional: Installing OpenAI's Whisper

If you plan on using a local installation of OpenAI's Whisper for transcribing audio to text, you'll need to set it up separately. Detailed installation instructions for Whisper can be found in the [official Whisper repository](https://github.com/openai/whisper). 

If you prefer to use OpenAI's Whisper API for transcriptions, you do not need a local installation. You can obtain an API key for this purpose from [OpenAI's API key page](https://platform.openai.com/account/api-keys).

## Configuration

To use ElevenLabs you need to get an API Key. You can get one for free, but they do limit how many characters you can translate before you need to pay.

To use this application, you need to set the environment variable:
ELEVENLABS_API_KEY
to the API key you've gotten from ElevenLabs

## Usage

Run the main.py script to start the application:

```bash
python main.py
```

You'll see a long table of translations in the middle column of the screen.

Choose "Synthesize Voices" and you'll see voice control options below, and the Voice selection drop-down will become active.

First: Select a voice

Second: Click on the translation you'd like to preview (from the scrolling table)

When you do that, the translated text should appear in the text box.

Third: If you want to hear how the translation is vocalized, simply press "Generate Speech".

You can also edit the translated speech by adding embedded tags like <break> for pauses.

And modify the translated speech using the provided sliders.

## License

This project is licensed under the terms of the MIT license.
Serious kudos to winedarkmoon who wrote the underlying code.


​
