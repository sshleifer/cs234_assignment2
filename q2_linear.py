import tensorflow as tf
import tensorflow.contrib.layers as layers

from utils.general import get_logger
from utils.test_env import EnvTest
from core.deep_q_learning import DQN
from q1_schedule import LinearExploration, LinearSchedule

from configs.q2_linear import config


class Linear(DQN):
    """
    Implement Fully Connected with Tensorflow
    """
    def add_placeholders_op(self):
        """
        Adds placeholders to the graph

        These placeholders are used as inputs to the rest of the model and will be fed
        data during training.
        """
        # this information might be useful
        c = self.config
        batch_dim_size = None
        height, width, n_chan = list(self.env.observation_space.shape)
        self.s = tf.placeholder(
            tf.uint8, (batch_dim_size, height, width, n_chan * c.state_history)
        )
        self.a = tf.placeholder(tf.int32, (batch_dim_size))
        self.r = tf.placeholder(tf.float32, (batch_dim_size))
        self.sp = tf.placeholder(tf.uint8, (batch_dim_size, height, width, n_chan * c.state_history))
        self.done_mask = tf.placeholder(tf.bool, (batch_dim_size))
        self.lr = tf.placeholder(tf.float32, shape=[])


        ##############################################################
        """
        TODO: 
            Add placeholders:
            Remember that we stack 4 consecutive frames together.
                - self.s: batch of states, type = uint8
                    shape = (batch_size, img height, img width, nchannels x config.state_history)
                - self.a: batch of actions, type = int32
                    shape = (batch_size)
                - self.r: batch of rewards, type = float32
                    shape = (batch_size)
                - self.sp: batch of next states, type = uint8
                    shape = (batch_size, img height, img width, nchannels x config.state_history)
                - self.done_mask: batch of done, type = bool
                    shape = (batch_size)
                - self.lr: learning rate, type = float32
        
        (Don't change the variable names!)
        
        HINT: 
            Variables from config are accessible with self.config.variable_name.
            Check the use of None in the dimension for tensorflow placeholders.
            You can also use the state_shape computed above.
        """

    def get_q_values_op(self, state, scope, reuse=False):
        """
        Returns Q values for all actions

        Args:
            state: (tf tensor) 
                shape = (batch_size, img height, img width, nchannels x config.state_history)
            scope: (string) scope name, that specifies if target network or not
            reuse: (bool) reuse of variables in the scope

        Returns:
            out: (tf tensor) of shape = (batch_size, num_actions)
        """
        # this information might be useful
        num_actions = self.env.action_space.n
        with tf.variable_scope(scope, reuse=reuse) as vs:
            # TODO?: use  - tf.layers.flatten
            flat_state = tf.contrib.layers.flatten(state)
            out = tf.layers.dense(flat_state, num_actions, use_bias=True)
        return out

        ##############################################################
        """
        TODO: 
            Implement a fully connected with no hidden layer (linear
            approximation with bias) using tensorflow.

        HINT: 
            - You may find the following functions useful:
                - tf.layers.flatten
                - tf.layers.dense

            - Make sure to also specify the scope and reuse
        """

    def add_update_target_op(self, q_scope, target_q_scope):
        """
        update_target_op will be called periodically 
        to copy Q network weights to target Q network

        Remember that in DQN, we maintain two identical Q networks with
        2 different sets of weights. In tensorflow, we distinguish them
        with two different scopes. If you're not familiar with the scope mechanism
        in tensorflow, read the docs
        https://www.tensorflow.org/programmers_guide/variable_scope

        Periodically, we need to update all the weights of the Q network 
        and assign them with the values from the regular network. 
        Args:
            q_scope: (string) name of the scope of variables for q
            target_q_scope: (string) name of the scope of variables
                        for the target network
        """
        ##############################################################
        """
        TODO: 
            Add an operator self.update_target_op that for each variable in
            tf.GraphKeys.GLOBAL_VARIABLES that is in q_scope, assigns its
            value to the corresponding variable in target_q_scope

        HINT: 
            You may find the following functions useful:
                - tf.get_collection
                - tf.assign
                - tf.group (the * operator can be used to unpack a list)

        (be sure that you set self.update_target_op)
        """
        sorted_q_vars = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, q_scope)
        sorted_targ_vars = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, target_q_scope)
        # TODO(SS): do we need to sort?
        zipped = zip(sorted_q_vars, sorted_targ_vars)
        self.update_target_op = tf.group(*[tf.assign(a,b) for a, b in zipped])
        ################### YOUR CODE HERE - 5-10 lines #############


    def add_loss_op(self, q, target_q):
        """
        Sets the loss of a batch, self.loss is a scalar

        Args:
            q: (tf tensor) shape = (batch_size, num_actions)
            target_q: (tf tensor) shape = (batch_size, num_actions)
        """
        # you may need this variable
        num_actions = self.env.action_space.n
        not_done_mask = 1 - tf.cast(self.done_mask, tf.float32)
        future_rewards = (not_done_mask * self.config.gamma * tf.reduce_max(target_q, axis=1))
        qsamp = self.r + future_rewards
        deltas = tf.squared_difference(qsamp, q)
        self.loss = tf.reduce_mean(deltas)

        #future_rewards_if_not_done = tf.

        ##############################################################
        """
        TODO: 
            The loss for an example is defined as:
                Q_samp(s) = r if done
                          = r + gamma * max_a' Q_target(s', a')
                loss = (Q_samp(s) - Q(s, a))^2 
        HINT: 
            - Config variables are accessible through self.config
            - You can access placeholders like self.a (for actions)
                self.r (rewards) or self.done_mask for instance
            - You may find the following functions useful
                - tf.cast
                - tf.reduce_max
                - tf.reduce_sum
                - tf.one_hot
                - tf.squared_difference
                - tf.reduce_mean
        """
        ##############################################################
        ##################### YOUR CODE HERE - 4-5 lines #############
        pass

        ##############################################################
        ######################## END YOUR CODE #######################


    def add_optimizer_op(self, scope):
        """
        Set self.train_op and self.grad_norm
        Args:
            scope: (string) scope name, that specifies if target network or not
        """
        all_variables = tf.trainable_variables()
        scope_variables = tf.contrib.framework.filter_variables(all_variables, include_patterns=[scope])

        optimizer = tf.train.AdamOptimizer(learning_rate=self.lr)
        gvs = optimizer.compute_gradients(self.loss, var_list=scope_variables)
        if self.config.grad_clip:
            gvs = [(tf.clip_by_norm(grad, config.clip_val), var)
                       for grad, var in gvs]

        self.train_op = optimizer.apply_gradients(gvs)
        self.grad_norm = tf.global_norm([x for x in gvs if x is not None])
        ##############################################################
        """
        TODO: 
            1. get Adam Optimizer
            2. compute grads with respect to variables in scope for self.loss
            3. if self.config.grad_clip is True, then clip the grads
                by norm using self.config.clip_val 
            4. apply the gradients and store the train op in self.train_op
                (sess.run(train_op) must update the variables)
            5. compute the global norm of the gradients (which are not None) and store 
                this scalar in self.grad_norm

        HINT: you may find the following functions useful
            - tf.get_collection
            - optimizer.compute_gradients
            - tf.clip_by_norm
            - optimizer.apply_gradients
            - tf.global_norm
             
             you can access config variables by writing self.config.variable_name
        """
        ##############################################################
        #################### YOUR CODE HERE - 8-12 lines #############

        pass
        
        ##############################################################
        ######################## END YOUR CODE #######################
    


if __name__ == '__main__':
    env = EnvTest((5, 5, 1))

    # exploration strategy
    exp_schedule = LinearExploration(env, config.eps_begin, 
            config.eps_end, config.eps_nsteps)

    # learning rate schedule
    lr_schedule  = LinearSchedule(config.lr_begin, config.lr_end,
            config.lr_nsteps)

    # train model
    model = Linear(env, config)
    model.run(exp_schedule, lr_schedule)
