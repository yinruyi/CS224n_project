import cPickle
import numpy as np
import os
import random

def get_batches(config_obj):
    batch_size = config_obj.batch_size

    caption_length_2_caption_ids =\
            cPickle.load(open("coco/data/train_caption_length_2_caption_ids"))
    caption_length_2_no_of_captions =\
            cPickle.load(open("coco/data/train_caption_length_2_no_of_captions"))

    # group all caption ids in batches:
    batches_of_caption_ids = []
    for caption_length in caption_length_2_no_of_captions:
        caption_ids = caption_length_2_caption_ids[caption_length]
        # randomly shuffle the order of the caption ids:
        random.shuffle(caption_ids)
        no_of_captions = caption_length_2_no_of_captions[caption_length]
        no_of_full_batches = int(no_of_captions/batch_size)

        # add all full batches to batches_of_caption_ids:
        for i in range(no_of_full_batches):
            batch_caption_ids = caption_ids[i*batch_size:(i+1)*batch_size]
            batches_of_caption_ids.append(batch_caption_ids)

        # get the remaining caption ids and add to batches_of_captions (not a
        # full batch, i.e, it will contain fewer than "batch_size" captions):
        #batch_caption_ids = caption_ids[no_of_full_batches*batch_size:]
        #batches_of_caption_ids.append(batch_caption_ids)

    # randomly shuffle the order of the batches:
    random.shuffle(batches_of_caption_ids)

    return batches_of_caption_ids

def get_batch_ph_data(batch_caption_ids, config_obj, caption_id_2_img_id,
            train_img_id_2_feature_vector, train_caption_id_2_caption):
    # get the dimension parameters:
    batch_size = config_obj.batch_size
    img_dim = config_obj.img_dim
    caption_length = len(train_caption_id_2_caption[batch_caption_ids[0]])

    captions = np.zeros((batch_size, caption_length))
    # (row i of captions will be the tokenized caption for ex i in the batch)
    img_vectors = np.zeros((batch_size, img_dim))
    # (row i of img_vectors will be the img feature vector for ex i in the batch)
    labels = -np.ones((batch_size, caption_length + 1))
    # (row i of labels will be the targets for ex i in the batch)

    # pupulate the return data:
    for i in range(len(batch_caption_ids)):
        caption_id = batch_caption_ids[i]
        img_id = caption_id_2_img_id[caption_id]
        img_vector = train_img_id_2_feature_vector[img_id]
        caption = train_caption_id_2_caption[caption_id]

        captions[i] = caption
        img_vectors[i] = img_vector
        labels[i, 1:caption_length] = caption[1:]

        # example to explain labels:
        # caption == [<SOS>, a, cat, <EOS>]
        # caption_length == 4
        # labels[i] == [-1, -1, -1, -1, -1]
        # caption[1:] == [a, cat, <EOS>]
        # labels[i, 1:caption_length] = caption[1:] gives:
        # labels[i] == [-1, a, cat, <EOS>, -1]
        # corresponds to the input:
        # img, <SOS>, a, cat, <EOS>
        # img: no prediciton should be made (-1)
        # <SOS>: should predict a (a)
        # a: should predict cat (cat)
        # cat: should predict <EOS> (<EOS>)
        # <EOS>: no prediction should be made (-1)

    return captions, img_vectors, labels

def train_data_iterator(config_obj):
    # get the batches of caption ids:
    batches_of_caption_ids = get_batches(config_obj)

    # load data to map from caption id to img feature vector:
    caption_id_2_img_id = cPickle.load(open("coco/data/caption_id_2_img_id"))
    train_img_id_2_feature_vector =\
                cPickle.load(open("coco/data/train_img_id_2_feature_vector"))
    # load data to map from caption id to caption:
    train_caption_id_2_caption =\
                cPickle.load(open("coco/data/train_caption_id_2_caption"))

    for batch_of_caption_ids in batches_of_caption_ids:
        # get the batch's data in a format ready to be fed into the placeholders:
        captions, img_vectors, labels = get_batch_ph_data(batch_of_caption_ids,
                    config_obj, caption_id_2_img_id,
                    train_img_id_2_feature_vector, train_caption_id_2_caption)

        # yield the data to enable iteration (will be able to do:
        # for captions, img_vector, labels in train_data_iterator(config):)
        yield (captions, img_vectors, labels)
