# Voice helper

What it is: a microphone button and an "i" button in the top bar of every page, and on the first Carryover page. It does what the buttons do, by voice. The "i" button explains how it works.

Where AI is used, and where it is not
- Speech to text uses AI. The browser's built in speech recognition, a machine learning model run by the browser maker (Google in Chrome, Apple in Safari), turns the voice into words. Carryover sends it no prompt and does not choose or change the model. While the microphone is on, the audio goes to that speech service. Carryover does not record or keep the audio.
- Command matching does not use AI. Once the words come back, plain code matches them to the buttons on screen and to a fixed list of commands. There is no language model, no system prompt and no persona at this step, so it cannot make anything up.

How it turns on: tap the microphone once. The browser asks for permission first (allow once, or while visiting the site). After that it listens from page to page until it is tapped again, or after 3 minutes with nothing said. It shows no transcript and no pop ups while listening. The page simply does what was asked.

What it does: it presses any button or choice whose words are spoken (continue, next, skip, sky, slow, heat a meal) and also understands actions: next step, show the small steps, read it again, pause, play, I need help, take a break, go home, my tasks, settings, go back, all steps, information, close, and opening a task by name or number. The wording does not have to be exact, and it uses the browser's best few guesses at the words. If an action needs the person to be somewhere else, it takes them there first. While the app is reading a step aloud, only short control words (pause, play, read again, help, break, back, home, tasks) are accepted, so the reading does not trigger commands.

It never marks a step done on its own. When someone says next or done on a step, it asks "Did you finish this step?" out loud and shows Yes and Not yet. Only a yes (spoken, or the Yes button) runs the normal Done button, so the data logged is the same as a tap. It never presses buttons that change or erase things, such as Redo first time setup or Reset.

Privacy: the microphone is off until the person turns it on. The browser shows when it is on, the icon shows it is on, and it turns off by itself after 3 minutes of nothing said. Nothing the person says is stored by Carryover.

Limits: it needs Chrome or Safari and a microphone. The commands are a fixed set with flexible wording, so a phrase outside the set may not work. A later version could use a language model, only with the person's consent.
