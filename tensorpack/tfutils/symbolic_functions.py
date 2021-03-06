# -*- coding: UTF-8 -*-
# File: symbolic_functions.py
# Author: Yuxin Wu <ppwwyyxx@gmail.com>

import tensorflow as tf
import numpy as np
from ..utils import logger

def one_hot(y, num_labels):
    """
    :param y: prediction. an Nx1 int tensor.
    :param num_labels: an int. number of output classes
    :returns: an NxC onehot matrix.
    """
    logger.warn("symbf.one_hot is deprecated in favor of more general tf.one_hot")
    return tf.one_hot(y, num_labels, 1.0, 0.0, name='one_hot')

def prediction_incorrect(logits, label, topk=1):
    """
    :param logits: NxC
    :param label: N
    :returns: a float32 vector of length N with 0/1 values, 1 meaning incorrect prediction
    """
    return tf.cast(tf.logical_not(tf.nn.in_top_k(logits, label, topk)), tf.float32)

def flatten(x):
    """
    Flatten the tensor.
    """
    return tf.reshape(x, [-1])

def batch_flatten(x):
    """
    Flatten the tensor except the first dimension.
    """
    shape = x.get_shape().as_list()[1:]
    if None not in shape:
        return tf.reshape(x, [-1, np.prod(shape)])
    return tf.reshape(x, tf.pack([tf.shape(x)[0], -1]))

def logSoftmax(x):
    """
    Batch log softmax.
    :param x: NxC tensor.
    :returns: NxC tensor.
    """
    with tf.op_scope([x], 'logSoftmax'):
        z = x - tf.reduce_max(x, 1, keep_dims=True)
        logprob = z - tf.log(tf.reduce_sum(tf.exp(z), 1, keep_dims=True))
        return logprob

def class_balanced_binary_class_cross_entropy(pred, label, name='cross_entropy_loss'):
    """
    The class-balanced cross entropy loss for binary classification,
    as in `Holistically-Nested Edge Detection
    <http://arxiv.org/abs/1504.06375>`_.

    :param pred: size: b x ANYTHING. the predictions in [0,1].
    :param label: size: b x ANYTHING. the ground truth in {0,1}.
    :returns: class-balanced binary classification cross entropy loss
    """
    z = batch_flatten(pred)
    y = tf.cast(batch_flatten(label), tf.float32)

    count_neg = tf.reduce_sum(1. - y)
    count_pos = tf.reduce_sum(y)
    beta = count_neg / (count_neg + count_pos)

    eps = 1e-8
    loss_pos = -beta * tf.reduce_mean(y * tf.log(tf.abs(z) + eps), 1)
    loss_neg = (1. - beta) * tf.reduce_mean((1. - y) * tf.log(tf.abs(1. - z) + eps), 1)
    cost = tf.sub(loss_pos, loss_neg)
    cost = tf.reduce_mean(cost, name=name)
    return cost

def print_stat(x):
    """ a simple print op.
        Use it like: x = print_stat(x)
    """
    return tf.Print(x, [tf.reduce_mean(x), x], summarize=20)

def rms(x, name=None):
    if name is None:
        name = x.op.name + '/rms'
    return tf.sqrt(tf.reduce_mean(tf.square(x)), name=name)
