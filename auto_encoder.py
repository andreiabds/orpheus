from data_format import build_nn_dataset
from keras.layers import Input, Dense
from keras.models import Model

class Trainer():

    def __init__(self):
        print "Building datasets..."
        nn_input, nn_output = build_nn_dataset()
        print "Finished building datasets!"


#list of hidden node sizes
    def train_nn(self, embedding_size=32):

        INPUT_SHAPE = nn_input.shape[1]

        # this is the size of our encoded representations
         # 32 floats -> compression of factor 637.625, assuming the input is 20404 floats

        ##write in functions
        #include passing a list of node sizes
        #try to design a more complicated auto encoder
        #try to get smaller error
        #goal: get a good embedding space

        # this is our input placeholder
        input_song = Input(shape=(nn_input.shape[1],))
        # "encoded" is the encoded representation of the input
        encoded = Dense(embedding_size, activation='relu')(input_song)
        # "decoded" is the lossy reconstruction of the input
        decoded = Dense(nn_input.shape[1], activation='linear')(encoded)

        # this model maps an input to its reconstruction
        autoencoder = Model(input=input_song, output=decoded)

        # this model maps an input to its encoded representation
        encoder = Model(input=input_song, output=encoded)

        # create a placeholder for an encoded (32-dimensional) input
        encoded_input = Input(shape=(embedding_size,))
        # retrieve the last layer of the autoencoder model
        decoder_layer = autoencoder.layers[-1]
        # create the decoder model
        decoder = Model(input=encoded_input, output=decoder_layer(encoded_input))

        autoencoder.compile(optimizer='sgd', loss='mean_squared_error')

        autoencoder.fit(nn_input, nn_input,
                        nb_epoch=1,
                        batch_size=64,
                        shuffle=True)

        autoencoder.fit(nn_input, nn_input,
                        nb_epoch=1,
                        batch_size=512,
                        shuffle=True)


        # encode and decode some digits
        # note that we take them from the *test* set
        encoded_songs = encoder.predict(nn_input)
        # decoded_songs = decoder.predict(encoded_songs)
        final_prediction = autoencoder.predict(nn_input)
