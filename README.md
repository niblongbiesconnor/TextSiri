TextSiri
---

## TextSiri has been completely rewritten and none of the modules are compatible. I am going to rewrite them to be compatible soon.

TextSiri is an IRC bot with outstanding modularity. All of its power comes from **modules**, a new way to add commands to your bot! Simply throw all of your modules to the **modules** folder, and you are set!

Requirements
---

 - Python 3
 - irclib 13
 - Requests

These packages can be installed by running *pip -r install requirements.txt*
Configuration
---

When you first run TextSiri it will create a new file for you called **config.cfg**. All of the bot's behavior can be changed from here. This is also where your bot's modules' configuration stays. Keep it safe!

Modules
---

All of the modules that I have created can be found [here](http://github.com/mission712/textsiri-modules). Simply throw them in the **modules** directory. They will automatically create their configuration files, and you may change them while the bot's running (Feature of the *Reload* module).

License
---

This work is now licensed under the **MIT License**. You may obtain, modify and share this software as long as you give me credits for substantial portions of code.
