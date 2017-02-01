from data_format import build_nn_dataset
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.regularizers import l2
from keras import backend as K
from keras.layers.core import Dropout

print "Building datasets..."
nn_input, nn_output = build_nn_dataset()
print "Finished building datasets!"


X_train = nn_input
Y_train = nn_output
X_test = nn_input
Y_test = nn_output

#datframe with song lyricist composer prediction
#calculate precision
#hook it to keras
#make it print after every epoch

#TensorBoard Callback to make graphs
#PRINT PRECISION ON TENSORBOARD!!!!!!!!!!
#SPLIT TRAIN AND TEST



NUM_HIDDEN_LAYERS = 3
model = Sequential()


#input layer
model.add(Dense(output_dim=64, input_dim=nn_input.shape[1]))
model.add(Activation("relu"))

#hidden layers
for i in xrange(NUM_HIDDEN_LAYERS):
    model.add(Dense(output_dim=64, W_regularizer = l2(.01)))
    model.add(Activation("relu"))
    model.add(keras.layers.core.Dropout(0.5))


#http://stats.stackexchange.com/questions/207794/what-loss-function-for-multi-class-multi-label-classification-tasks-in-neural-n

#output layer
model.add(Dense(output_dim=nn_output.shape[1]))
model.add(Activation("sigmoid"))


#model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])



model.fit(X_train, Y_train, nb_epoch=100, batch_size=32)
loss_and_metrics = model.evaluate(X_test, Y_test, batch_size=32)


pred_outputs = model.predict(X_test, batch_size=32, verbose=0)


def predicted_composers(pred_out):
    return np.argmax(pred_out[:,:887],axis=1)

def predicted_lyricists(pred_out):
    return np.argmax(pred_out[:,887:],axis=1)

# with a Sequential model
# get_nextolast_layer_output = K.function([model.layers[0].input],
#                                   [model.layers[NUM_HIDDEN_LAYERS-1].output])
# embeddings = get_nextolast_layer_output([X_test])[0]

