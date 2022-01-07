from __future__ import unicode_literals, print_function, division
import random
from pathlib import Path

from app.services.pytorch import *
from app.main import workspace, name, source, target, device, input_lang_name, output_lang_name

#########################################################################
# GLOBAL VARS
#########################################################################

# training parameters
print_every = 1000
iters = [
    {"lr": 0.01, "nb": 50000},
    {"lr": 0.003, "nb": 50000},
    {"lr": 0.001, "nb": 50000},
]

model_image = ""  # empty for new model
#########################################################################
# MAIN
#########################################################################

if __name__ == "__main__":

    path_source = Path(workspace).joinpath(name, source)
    path_target = Path(workspace).joinpath(name, target)
    path_target.mkdir(parents=True, exist_ok=True)

    # making Lang dictionnaries

    input_lang, output_lang, pairs = prepareData(
        input_lang_name, output_lang_name, path_source, False
    )

    random.shuffle(pairs)
    for p in pairs[:20]:
        print(p)

    print("input_lang", input_lang.word2index)
    print("output_lang", output_lang.word2index)

    save_lang(input_lang, output_lang, path_target)

    # train model

    if model_image == "":
        print(f"will train new seq2seq model {input_lang.name}/{output_lang.name}")
        encoder, attn_decoder = new_seq2seq_model(input_lang, output_lang)
    else:
        learning_rate = 0.01
        print(
            f"will train on {path_target}/{model_image} seq2seq model {input_lang.name}/{output_lang.name}"
        )
        model = path_target.joinpath(model_image)
        print(model)
        (
            encoder,
            attn_decoder,
            encoder_optimizer,
            decoder_optimizer,
        ) = load_pytorch_checkpoint(
            model, input_lang, output_lang, device, hidden_size, learning_rate
        )

    for iter in iters:
        learning_rate = iter["lr"]
        training_iters = iter["nb"]
        print(f"training {training_iters} iters with learning rate: {learning_rate}")
        trainIters(
            encoder,
            attn_decoder,
            pairs,
            training_iters,
            path_target,
            input_lang,
            output_lang,
            print_every=print_every,
            learning_rate=learning_rate,
        )
        evaluateRandomly(encoder, attn_decoder, input_lang, output_lang, pairs)
        findBadPreds(encoder, attn_decoder, input_lang, output_lang, pairs, n=100)
