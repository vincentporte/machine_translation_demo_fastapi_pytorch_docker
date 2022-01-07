from __future__ import unicode_literals, print_function, division
from io import open
import random

import time
import math

from pathlib import Path
from datetime import datetime
import dill

import matplotlib.pyplot as plt

plt.switch_backend("agg")
import matplotlib.ticker as ticker
import numpy as np

import torch
import torch.nn as nn
from torch import optim
import torch.nn.functional as F

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# langs parameters
SOS_token = 0
EOS_token = 1
MAX_LENGTH = 150

# training parameters
teacher_forcing_ratio = 0.5
hidden_size = 512
dropout_p = 0.1

#########################################################################
# LANG CLASS
#########################################################################


class Lang2:
    def __init__(self, name):
        self.name = name

        # init dicts
        # characters = list("0123456789abcdefghijklmnopqrstuvwxyz+.:,*/=;-")
        characters = list("0123456789abcdefghijklmnopqrstuvwxyz+.,:")
        print(characters)
        self.word2index = {c: i + 2 for i, c in enumerate(characters)}
        self.word2count = {c: 0 for i, c in enumerate(characters)}
        self.index2word = {0: "SOS", 1: "EOS"}
        self.index2word.update({i + 2: c for i, c in enumerate(characters)})
        self.n_words = len(self.index2word.keys())

    def addSentence(self, sentence):
        # making dict at character level
        for item in list(sentence):
            self.addWord(item)

    def addWord(self, word):
        if word not in self.word2index:
            # print(f"adding {word} in {self.name}")
            self.word2index[word] = self.n_words
            self.word2count[word] = 1
            self.index2word[self.n_words] = word
            self.n_words += 1
        else:
            self.word2count[word] += 1


#########################################################################
# RNN CLASS
#########################################################################


class EncoderRNN2(nn.Module):
    def __init__(self, input_size, hidden_size):
        super(EncoderRNN2, self).__init__()
        self.hidden_size = hidden_size

        self.embedding = nn.Embedding(input_size, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size)

    def forward(self, input, hidden):
        embedded = self.embedding(input).view(1, 1, -1)
        output = embedded
        output, hidden = self.gru(output, hidden)
        return output, hidden

    def initHidden(self):
        return torch.zeros(1, 1, self.hidden_size, device=device)


class AttnDecoderRNN2(nn.Module):
    def __init__(
        self, hidden_size, output_size, dropout_p=dropout_p, max_length=MAX_LENGTH
    ):
        super(AttnDecoderRNN2, self).__init__()
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.dropout_p = dropout_p
        self.max_length = max_length

        self.embedding = nn.Embedding(self.output_size, self.hidden_size)
        self.attn = nn.Linear(self.hidden_size * 2, self.max_length)
        self.attn_combine = nn.Linear(self.hidden_size * 2, self.hidden_size)
        self.dropout = nn.Dropout(self.dropout_p)
        self.gru = nn.GRU(self.hidden_size, self.hidden_size)
        self.out = nn.Linear(self.hidden_size, self.output_size)

    def forward(self, input, hidden, encoder_outputs):
        embedded = self.embedding(input).view(1, 1, -1)
        embedded = self.dropout(embedded)

        attn_weights = F.softmax(
            self.attn(torch.cat((embedded[0], hidden[0]), 1)), dim=1
        )
        attn_applied = torch.bmm(
            attn_weights.unsqueeze(0), encoder_outputs.unsqueeze(0)
        )

        output = torch.cat((embedded[0], attn_applied[0]), 1)
        output = self.attn_combine(output).unsqueeze(0)

        output = F.relu(output)
        output, hidden = self.gru(output, hidden)

        output = F.log_softmax(self.out(output[0]), dim=1)
        return output, hidden, attn_weights

    def initHidden(self):
        return torch.zeros(1, 1, self.hidden_size, device=device)


#########################################################################
# GENERIC FUNCTIONS
#########################################################################


def asMinutes(s):
    m = math.floor(s / 60)
    s -= m * 60
    return "%dm %ds" % (m, s)


def timeSince(since, percent):
    now = time.time()
    s = now - since
    es = s / (percent)
    rs = es - s
    return "%s (- %s)" % (asMinutes(s), asMinutes(rs))


def showPlot(points):
    plt.figure()
    fig, ax = plt.subplots()
    # this locator puts ticks at regular intervals
    loc = ticker.MultipleLocator(base=0.2)
    ax.yaxis.set_major_locator(loc)
    plt.plot(points)


#########################################################################
# DATA PREPARATION FUNCTIONS
#########################################################################


def readlines_fromdir(path):
    lines = []
    for x in path.iterdir():
        if x.is_file():
            lines += open(x, encoding="utf-8").read().strip().split("\n")
    return lines


def readLangs(lang1, lang2, path, reverse=False):
    print("Reading lines...")

    # Read the file and split into lines
    lines = readlines_fromdir(path)

    # Split every line into pairs and normalize
    pairs = [[s.replace("\xa0", " ") for s in l.split("\t")] for l in lines]

    # Reverse pairs, make Lang instances
    if reverse:
        pairs = [list(reversed(p)) for p in pairs]
        input_lang = Lang2(lang2)
        output_lang = Lang2(lang1)
    else:
        input_lang = Lang2(lang1)
        output_lang = Lang2(lang2)

    return input_lang, output_lang, pairs


def prepareData(lang1, lang2, path, reverse=False):
    input_lang, output_lang, pairs = readLangs(lang1, lang2, path, reverse)
    print("Read %s sentence pairs" % len(pairs))
    # pairs = filterPairs(pairs)
    # print("Trimmed to %s sentence pairs" % len(pairs))
    print("Counting words...")
    for pair in pairs:
        input_lang.addSentence(pair[0])
        output_lang.addSentence(pair[1])
    print("Counted words:")
    print(input_lang.name, input_lang.n_words)
    print(output_lang.name, output_lang.n_words)
    return input_lang, output_lang, pairs


def indexesFromSentence(lang, sentence):
    return [
        lang.word2index[word]
        if word in lang.word2index.keys()
        else lang.word2index[" "]
        for word in list(sentence)
    ]
    # return [lang.word2index[word] for word in list(sentence)]


def tensorFromSentence(lang, sentence):
    indexes = indexesFromSentence(lang, sentence)
    indexes.append(EOS_token)
    return torch.tensor(indexes, dtype=torch.long, device=device).view(-1, 1)


def tensorsFromPair(pair, input_lang, output_lang):
    input_tensor = tensorFromSentence(input_lang, pair[0])
    target_tensor = tensorFromSentence(output_lang, pair[1])
    return (input_tensor, target_tensor)


#########################################################################
# TRAINING FUNCTIONS
#########################################################################


def train(
    input_tensor,
    target_tensor,
    encoder,
    decoder,
    encoder_optimizer,
    decoder_optimizer,
    criterion,
    max_length=MAX_LENGTH,
):
    encoder_hidden = encoder.initHidden()

    encoder_optimizer.zero_grad()
    decoder_optimizer.zero_grad()

    input_length = input_tensor.size(0)
    target_length = target_tensor.size(0)

    encoder_outputs = torch.zeros(max_length, encoder.hidden_size, device=device)

    loss = 0

    for ei in range(input_length):
        encoder_output, encoder_hidden = encoder(input_tensor[ei], encoder_hidden)
        encoder_outputs[ei] = encoder_output[0, 0]

    decoder_input = torch.tensor([[SOS_token]], device=device)

    decoder_hidden = encoder_hidden

    use_teacher_forcing = True if random.random() < teacher_forcing_ratio else False

    if use_teacher_forcing:
        # Teacher forcing: Feed the target as the next input
        for di in range(target_length):
            decoder_output, decoder_hidden, decoder_attention = decoder(
                decoder_input, decoder_hidden, encoder_outputs
            )
            loss += criterion(decoder_output, target_tensor[di])
            decoder_input = target_tensor[di]  # Teacher forcing

    else:
        # Without teacher forcing: use its own predictions as the next input
        for di in range(target_length):
            decoder_output, decoder_hidden, decoder_attention = decoder(
                decoder_input, decoder_hidden, encoder_outputs
            )
            topv, topi = decoder_output.topk(1)
            decoder_input = topi.squeeze().detach()  # detach from history as input

            loss += criterion(decoder_output, target_tensor[di])
            if decoder_input.item() == EOS_token:
                break

    loss.backward()

    encoder_optimizer.step()
    decoder_optimizer.step()

    return loss.item() / target_length


def trainIters(
    encoder,
    decoder,
    pairs,
    n_iters,
    path,
    input_lang,
    output_lang,
    print_every=1000,
    plot_every=100,
    learning_rate=0.01,
):
    start = time.time()
    plot_losses = []
    print_loss_total = 0  # Reset every print_every
    plot_loss_total = 0  # Reset every plot_every

    encoder_optimizer = optim.SGD(encoder.parameters(), lr=learning_rate)
    decoder_optimizer = optim.SGD(decoder.parameters(), lr=learning_rate)
    training_pairs = [
        tensorsFromPair(random.choice(pairs), input_lang, output_lang)
        for i in range(n_iters)
    ]
    criterion = nn.NLLLoss()

    for iter in range(1, n_iters + 1):
        training_pair = training_pairs[iter - 1]
        input_tensor = training_pair[0]
        target_tensor = training_pair[1]

        loss = train(
            input_tensor,
            target_tensor,
            encoder,
            decoder,
            encoder_optimizer,
            decoder_optimizer,
            criterion,
        )
        print_loss_total += loss
        plot_loss_total += loss

        if iter % print_every == 0:
            print_loss_avg = print_loss_total / print_every
            print_loss_total = 0
            print(
                "%s (%d %d%%) %.4f"
                % (
                    timeSince(start, iter / n_iters),
                    iter,
                    iter / n_iters * 100,
                    print_loss_avg,
                )
            )

            save_pytorch_checkpoint(
                encoder,
                decoder,
                encoder_optimizer,
                decoder_optimizer,
                path,
                print_loss_avg,
                input_lang,
                output_lang,
                learning_rate,
            )

        if iter % plot_every == 0:
            plot_loss_avg = plot_loss_total / plot_every
            plot_losses.append(plot_loss_avg)
            plot_loss_total = 0
            # print(f"trainIters, plotting on iter {iter} of {n_iters}, avg loss: {plot_loss_avg}")

    showPlot(plot_losses)


#########################################################################
# EVALUATION & PREDICTION FUNCTIONS
#########################################################################


def evaluate(
    encoder, decoder, input_lang, output_lang, sentence, max_length=MAX_LENGTH
):

    sentence = sentence[: max_length - 1]

    with torch.no_grad():
        input_tensor = tensorFromSentence(input_lang, sentence)
        input_length = input_tensor.size()[0]
        encoder_hidden = encoder.initHidden()

        encoder_outputs = torch.zeros(max_length, encoder.hidden_size, device=device)

        for ei in range(input_length):
            encoder_output, encoder_hidden = encoder(input_tensor[ei], encoder_hidden)
            encoder_outputs[ei] += encoder_output[0, 0]

        decoder_input = torch.tensor([[SOS_token]], device=device)  # SOS

        decoder_hidden = encoder_hidden

        decoded_words = []
        decoder_attentions = torch.zeros(max_length, max_length)

        for di in range(max_length):
            decoder_output, decoder_hidden, decoder_attention = decoder(
                decoder_input, decoder_hidden, encoder_outputs
            )
            decoder_attentions[di] = decoder_attention.data
            topv, topi = decoder_output.data.topk(1)
            if topi.item() == EOS_token:
                decoded_words.append("<EOS>")
                break
            else:
                decoded_words.append(output_lang.index2word[topi.item()])

            decoder_input = topi.squeeze().detach()

        return decoded_words, decoder_attentions[: di + 1]


# evaluate n pairs and display preds vs ground truth
def evaluateRandomly(encoder, decoder, input_lang, output_lang, pairs, n=10):
    for i in range(n):
        pair = random.choice(pairs)
        print(">", pair[0])
        print("=", pair[1])
        output_words, attentions = evaluate(
            encoder, decoder, input_lang, output_lang, pair[0]
        )
        output_sentence = "".join(output_words)
        print("<", output_sentence)
        print("")


# display n pairs if preds <> ground truth
def findBadPreds(encoder, decoder, input_lang, output_lang, pairs, n=100):
    for pair in pairs[:n]:
        output_words, attentions = evaluate(
            encoder, decoder, input_lang, output_lang, pair[0]
        )
        output_sentence = "".join(output_words)

        if output_sentence.rstrip("<EOS>") != pair[1]:
            print(">", pair[0])
            print("=", pair[1])
            print("<", output_sentence)
            print(" ")


#########################################################################
# MODEL & CLASSES management
#########################################################################


def save_lang(input_lang, output_lang, path):

    file = Path(path).joinpath(f"Lang_{input_lang.name}_{output_lang.name}.dill")

    # save non-model datas (Lang objects and list of keys)
    with open(file, "wb") as f:
        dill.dump(input_lang, f)
        dill.dump(output_lang, f)


def load_lang(input_lang_name, output_lang_name, path):
    file = Path(path).joinpath(f"Lang_{input_lang_name}_{output_lang_name}.dill")

    with open(file, "rb") as f:
        input_lang = dill.load(f)
        output_lang = dill.load(f)

    return input_lang, output_lang


def save_pytorch_checkpoint(
    encoder1,
    decoder1,
    encoder_optimizer,
    decoder_optimizer,
    path,
    loss,
    input_lang,
    output_lang,
    learning_rate,
):

    file = Path(path).joinpath(
        f"seq2seq_{input_lang.name}_{output_lang.name}_{encoder1.hidden_size}_{learning_rate}_{str(int(datetime.now().timestamp()))}_{loss:.5f}.dill"
    )
    # print(f"save_pytorch_checkpoint : {file}")

    # save model objects
    torch.save(
        {
            "encoder1_state_dict": encoder1.state_dict(),
            "decoder1_state_dict": decoder1.state_dict(),
            "encoder_optimizer_state_dict": encoder_optimizer.state_dict(),
            "decoder_optimizer_state_dict": decoder_optimizer.state_dict(),
        },
        file,
    )


def new_seq2seq_model(input_lang, output_lang):

    encoder = EncoderRNN2(input_lang.n_words, hidden_size).to(device)
    attn_decoder = AttnDecoderRNN2(
        hidden_size, output_lang.n_words, dropout_p=dropout_p
    ).to(device)

    return encoder, attn_decoder


def load_pytorch_checkpoint(
    path_model, input_lang, output_lang, device, hidden_size, learning_rate
):

    print(
        f"[{datetime.now()}] Loading pytorch seq2seq model with attention, device {device}"
    )

    checkpoint = torch.load(path_model, device)

    encoder1 = EncoderRNN2(input_lang.n_words, hidden_size).to(device)
    decoder1 = AttnDecoderRNN2(
        hidden_size, output_lang.n_words, dropout_p=dropout_p
    ).to(device)

    encoder1.load_state_dict(checkpoint["encoder1_state_dict"])
    decoder1.load_state_dict(checkpoint["decoder1_state_dict"])

    encoder_optimizer = optim.SGD(encoder1.parameters(), lr=learning_rate)
    decoder_optimizer = optim.SGD(decoder1.parameters(), lr=learning_rate)

    encoder_optimizer.load_state_dict(checkpoint["encoder_optimizer_state_dict"])
    decoder_optimizer.load_state_dict(checkpoint["decoder_optimizer_state_dict"])

    encoder1.eval()
    decoder1.eval()

    print(
        f"[{datetime.now()}]Pytorch seq2seq model with attention *for retraining* loaded"
    )

    return encoder1, decoder1, encoder_optimizer, decoder_optimizer


def load_pytorch_checkpoint_inference(
    path_model, input_lang, output_lang, device, hidden_size
):

    print(
        f"[{datetime.now()}] Loading {path_model} pytorch seq2seq model with attention, device {device}"
    )

    checkpoint = torch.load(path_model, device)

    encoder1 = EncoderRNN2(input_lang.n_words, hidden_size).to(device)
    decoder1 = AttnDecoderRNN2(
        hidden_size, output_lang.n_words, dropout_p=dropout_p
    ).to(device)

    encoder1.load_state_dict(checkpoint["encoder1_state_dict"])
    decoder1.load_state_dict(checkpoint["decoder1_state_dict"])

    encoder1.eval()
    decoder1.eval()

    print(
        f"[{datetime.now()}]Pytorch seq2seq model with attention *for inference* loaded"
    )

    return encoder1, decoder1
