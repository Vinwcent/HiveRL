# HiveRL

## The project

This project was a final project for the deep learning module of ESPCI Paris - PSL.
It is an implementation of the Hive Board game with a reinforcement learning algorithm inspired by AlphaZero and with a connection-based
representation of the game.

Here is a GIF of the generation of a game.

<img src="https://user-images.githubusercontent.com/91033856/235407976-13716e9d-2c0c-40f9-8aba-7562891547db.gif" width=50% height=50%>

You can find more informations about the algorithm on the following PDF

[main.pdf](https://github.com/Vinwcent/HiveRL/files/11363914/main.pdf)

## Resume training
If you have computational power and want to train it even further, look at the
```train.py``` file which will show you all you need. Basically you have 2
methods for the ```trainer```, the ```start_play``` which will make you play
against the currently loaded algorithm and the ```train``` one which will train and
save the model after each iteration of the training process.

You can also load a previous model thanks to the ```load_history_and_net```
method. There's already the latest weights and game histories of the pretraining
and training phase described in the PDF
