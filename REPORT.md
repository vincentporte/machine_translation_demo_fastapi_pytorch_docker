# Report

## purpose of the model
Convert raw entities into actionnables features in pricing neural network

For examples:
- 1/2 mat => couche demi mat
- c 1/2 mat => couche demi mat
- c demi mat => couche demi mat
- cdm => couche demi mat
- couche 1/2 mat => couche demi mat
- couche 1/2 mat certifie pefc 100% => couche demi mat
- fo a4 => format ouvert : 210.0 x 297.0 mm
- format a4 => format fini : 210.0 x 297.0 mm
- format ouvert : l.442 x h 210 mm => format ouvert : 442.0 x 210.0 mm
- ft 160 x 60 => format fini : 1600.0 x 600.0 mm
- 8.5 x 5.5 / => format fini : 85.0 x 55.0 mm
- 162x229 => format fini : 162.0 x 229.0 mm
- hauteur 2,5 cm x largeur 3,3 cm => format fini : 25.0 x 33.0 mm
- format 160 x 60 => format fini : 1600.0 x 600.0 mm

## iteratives steps
1. using regex
    - ok for 75%
    - but lots of mismatches = noise to train pricing

2. using state of the art (2019) seq2seq model with attention for translation
    - working on words
    - explosion of the number of tokens, especially the ones concerning dimensions

3. converting words seq2seq2 model with attention to char level model, using CNN char level model
    - limited tokens
    - dimensions compliant

## train the model
1. training datasets : see backend/datas/imprimeur/source
    - txt files containing translation pairs, separated by tabulation
    - easy to generate datas withs masks
2. before training
    - generate input and output langages : class Lang. See backend/app/services/pytorch
    - sentence is the entire pair (ie: format 160 x 60)
    - words are the unit part of the sentence. Here these are characters and some typographics one : * , ; etc...
3. training
    - 3 * 50000 iterations on training set, decreasing learning rate every 50000 iters : 0.01, 0.003 and 0.001
    - a bit of dropout for the style (0.1)
    - size of the embeddings in Encoder and Decoder : 512 
    - I decided not to split dataset between training set / test set / validation set. The corpus isn't infinite (although not manageable with regex :-D ), so that I don't care so much with overfitting.
    - obtain a loss = 0.0031
    - displaying random bad translations, at 0.0031, only rare occurences don't match with groundtruth

## what work well
* digit manipulation compliant
* easy to retrain, even on CPU :D
* ligthweight
* handle all raw entities in one pred request from API

## what not so good
* unfrequent dimensions badly handled, ie "format 154x963 mm" => "format fini : 145.0 x 93.0 mm" which is schocking for users :-/ maybe linked to overfitting. But I prefer manage efficiently all possible variations of frequent dimensions.
* incompatibility with quantities, ie "quantités : 5 x 1000 exs". Model mismatched with dimensions. So that, I setup a very light dedicated model for quantities (not included in the demo)

## what I like to do next
* train model to handle an entire request for quotation, without extracting named entities
* current situation
    - request = "urgent, devis pour 6000 flyers a5, quadri rv, cdm, sous film par paquet de 100, livraison 72, merci"
    - Named Entities extracted : 
        * "text": "6000", "entity": "EXEMPLAIRES"
        * "text": "flyers", "entity": "PRODUCT"
        * "text": "a5", "entity": "FORMAT"
        * "text": "quadri rv", "entity": "IMPRESSION" 
        * "text": "cdm", "entity": "PAPIER"
        * "text": "sous film par paquet de 100", "entity": "CONDITIONNEMENT"
        * "text": "livraison 72", "entity": "LIVRAISON"
    - Named Entities translated :
        * "text": "6000", "entity": "EXEMPLAIRES"
        * "text": "flyers", "entity": "PRODUCT"
        * "text": "format fini : 148.0 x 210.0 mm", "entity": "FORMAT"
        * "text": "recto : quadri, verso : quadri", "entity": "IMPRESSION"
        * "text": "couche demi mat", "entity": "PAPIER"
        * "text": "sous film par paquet de 100", "entity": "CONDITIONNEMENT"
        * "text": "livraison 72", "entity": "LIVRAISON"
* wished situation
    - request = "urgent, devis pour 6000 flyers a5, quadri rv, cdm, sous film par paquet de 100, livraison 72, merci"
    - translated request = "urgent, devis pour 6000 flyers format fini : 148.0 x 210.0 mm, recto : quadri, verso : quadri, couche demi mat, sous film par paquet de 100, livraison 72, merci"
* need to generate bigger dataset, using masks and all combinaison of items
* need bigger GPU or TPU