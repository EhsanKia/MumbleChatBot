MumbleChatBot
=============

Simple client written in Python that let's you create a bot and interact with a mumble server.
New version was written from the ground up and offers better API support for writing your bot.

The only dependency is [Twisted](http://twistedmatrix.com/trac/).

Currently, the client can:

- Auth and connect to a server using password or certificate
- Get user and channel states
- Get and send chat messages
- Get voice packets (through TCP only, UDP tunnel is not implemented yet)

There is no codec support though, so the audio data cannot be parsed.

A sample bot implementation is given in peebot.py
You can use it as a reference. It shows how to:

- Dynamically reload the bot
- Store and list user/channel list
- Move users around and change their state (mute/deafen)
- Recieve, parse and send text messages

Feel free to expand on and send me an e-mail for any question or suggestion.
