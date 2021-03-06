import tensorflow as tf
import logging


class PANOutput(object):
    def __init__(self, input_y, prev_layer, num_nodes_prev_layer, num_classes, l2_sum, l2_reg_lambda):
        if l2_sum is not None:
            self.l2_sum = l2_sum
            logging.warning("OPTIMIZING PROPER L2")
        else:
            self.l2_sum = tf.constant(0.0)
        # Final (unnormalized) scores and predictions
        with tf.variable_scope("output"):
            # W = tf.Variable(tf.truncated_normal([num_filters_total, num_classes], stddev=0.1), name="W")
            W = tf.get_variable(
                "W",
                shape=[num_nodes_prev_layer, num_classes],
                initializer=tf.contrib.layers.xavier_initializer())
            b = tf.Variable(tf.constant(0.1, shape=[num_classes]), name="b")

            if l2_reg_lambda > 0:
                self.l2_sum += tf.nn.l2_loss(W)
            # l2_loss += tf.nn.l2_loss(b)
            self.scores = tf.nn.xw_plus_b(prev_layer, W, b, name="scores")
            self.predictions = tf.argmax(self.scores, 1, name="predictions")

        # self.rate_percentage = [0.0] * num_classes
        # with tf.variable_scope("prediction-ratio"):
        #     for i in range(num_classes):
        #         rate1_logistic = tf.equal(self.predictions, i)
        #         self.rate_percentage[i] = tf.reduce_mean(tf.cast(rate1_logistic, "float"),
        #                                                  name="rate-" + str(i) + "/percentage")

        # CalculateMean cross-entropy loss
        with tf.variable_scope("loss-lbd" + str(l2_reg_lambda)):
            losses = tf.nn.softmax_cross_entropy_with_logits(labels=input_y, logits=self.scores)
            self.loss = tf.reduce_mean(losses) + l2_reg_lambda * self.l2_sum
        # Accuracy
        with tf.variable_scope("accuracy"):
            correct_predictions = tf.equal(self.predictions, tf.argmax(input_y, 1))
            self.accuracy = tf.reduce_mean(tf.cast(correct_predictions, "float"), name="accuracy")

