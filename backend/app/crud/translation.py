from pathlib import Path

from app.schemas.translation import (
    TranslationInSchema,
    TranslationOutSchema,
    EntitySchema,
)

from app.services.pytorch import evaluate

# loading dir names
from app.main import (
    seq2seq_input_lang,
    seq2seq_output_lang,
    seq2seq_encoder,
    seq2seq_decoder,
)


def translate_entity(entity: EntitySchema, input_lang, output_lang, encoder, decoder):

    if entity["entity"] in ["FORMAT", "GRAMMAGES", "PAPIER", "IMPRESSION", "PRODUCT"]:
        text = entity["entity"][:2] + "|" + entity["text"]
        output_chars, attentions = evaluate(
            encoder, decoder, input_lang, output_lang, text
        )
        entity["text"] = "".join(output_chars).rstrip("<EOS>")

    return EntitySchema(**entity)


async def translate_entities(entities: TranslationInSchema) -> TranslationOutSchema:

    ents = [ent.dict(exclude_unset=True) for ent in entities.entities]

    translation = []

    entities = list(
        map(
            lambda x: translate_entity(
                x,
                seq2seq_input_lang,
                seq2seq_output_lang,
                seq2seq_encoder,
                seq2seq_decoder,
            ),
            ents,
        )
    )

    return {"entities": entities}
