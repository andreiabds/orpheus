from data_format import build_nn_dataset
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.regularizers import l2
from keras import backend as K
from keras.layers.core import Dropout
from keras import initializations, optimizers
from keras.callbacks import TensorBoard
import datetime



class Trainer():

    def __init__(self):
        print "Building datasets..."
        nn_input, nn_output = build_nn_dataset()
        print "Finished building datasets!"
        self.model = None

        #train test split in the FUTURE
        self.X_train = nn_input
        self.X_test = nn_input




    def create_model(self, hidden_layers_sizes=[64,32,64], reg=0.001,
                     dropout=0.5, weight_scale=0.01, lr=0.0001):
        '''
        Creates the architecture of the neural netz.
        Embedding vector is the middle hidden layer.

        input, hidden layers and output
        '''
        #def weight_init(shape, name=None):
        #    return initializations.normal(shape, scale=weight_scale, name=name)


        def relu_6(x):
            return K.relu(x, max_value=6)

        INPUT_SIZE = self.X_train.shape[1]
        NUM_HIDDEN_LAYERS = len(hidden_layers_sizes)
        model = Sequential()

        #input layer
        #model.add(Dense(output_dim=hidden_layers_sizes[0], input_dim=INPUT_SIZE, init='weight_init'))
        model.add(Dense(output_dim=hidden_layers_sizes[0], input_dim=INPUT_SIZE, init='he_normal'))
        model.add(Activation(relu_6))

        #hidden layers
        for i, hidden_layer_size in enumerate(hidden_layers_sizes[1:]):
            #model.add(Dense(output_dim=hidden_layer_size, W_regularizer=l2(reg), init=weight_init))
            model.add(Dense(output_dim=hidden_layer_size, W_regularizer=l2(reg), init='he_normal'))
            model.add(Activation(relu_6))
            model.add(Dropout(dropout))

        #output layer
        #model.add(Dense(output_dim=INPUT_SIZE, init=weight_init))
        model.add(Dense(output_dim=INPUT_SIZE, init='he_normal'))
        model.add(Activation("linear"))

        adam = optimizers.Adam(lr=lr)
        model.compile(loss='mean_squared_error', optimizer=adam, metrics=['accuracy'])
        self.model = model

    def train_nn(self, num_epochs=5, batch_size=32):
        log_name = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        tb = TensorBoard(log_dir='/Users/andreiasodrenichols/galvanize/orpheus/logs/%s' % log_name,
            histogram_freq=0, write_graph=True, write_images=False)

        self.model.fit(self.X_train, self.X_train, nb_epoch=num_epochs, batch_size=batch_size,
                       callbacks=[tb])
        #loss_and_metrics = model.evaluate(self.X_test, self.X_test, batch_size=batch_size)


    def get_embeddings(self):
        embedding_vector_fn = K.function([self.model.layers[0].input, K.learning_phase()],
                                          [self.model.layers[len(self.model.layers)/2 + 1].output])

        embedding_vectors = embedding_vector_fn([self.X_test, 0])[0]

        return embedding_vectors



    def get_predictions(self, batch_size=32):
        pred_outputs = model.predict(self.X_test, batch_size=batch_size, verbose=0)
        return pred_outputs






