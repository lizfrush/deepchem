import unittest
import numpy as np
import tensorflow as tf
import deepchem as dc
import deepchem.models.tensorgraph.layers as layers
from deepchem.data import NumpyDataset
from deepchem.models.tensorgraph.models.text_cnn import default_dict


class TestEstimators(unittest.TestCase):
  """
  Test converting TensorGraphs to Estimators.
  """

  def test_multi_task_classifier(self):
    """Test creating an Estimator from a MultitaskClassifier."""
    n_samples = 10
    n_features = 3
    n_tasks = 2

    # Create a dataset and an input function for processing it.

    np.random.seed(123)
    X = np.random.rand(n_samples, n_features)
    y = np.zeros((n_samples, n_tasks))
    dataset = dc.data.NumpyDataset(X, y)

    def input_fn(epochs):
      x, y, weights = dataset.make_iterator(
          batch_size=n_samples, epochs=epochs).get_next()
      return {'x': x, 'weights': weights}, y

    # Create a TensorGraph model.

    model = dc.models.MultitaskClassifier(n_tasks, n_features, dropouts=0)

    # Create an estimator from it.

    x_col = tf.feature_column.numeric_column('x', shape=(n_features,))
    weight_col = tf.feature_column.numeric_column('weights', shape=(n_tasks,))

    def accuracy(labels, predictions, weights):
      return tf.metrics.accuracy(labels, tf.round(predictions), weights)

    metrics = {'accuracy': accuracy}
    estimator = model.make_estimator(
        feature_columns=[x_col], weight_column=weight_col, metrics=metrics)

    # Train the model.

    estimator.train(input_fn=lambda: input_fn(100))

    # Evaluate the model.

    results = estimator.evaluate(input_fn=lambda: input_fn(1))
    assert results['loss'] < 1e-4
    assert results['accuracy'] > 0.9

  def test_multi_task_regressor(self):
    """Test creating an Estimator from a MultitaskRegressor."""
    n_samples = 10
    n_features = 3
    n_tasks = 2

    # Create a dataset and an input function for processing it.

    np.random.seed(123)
    X = np.random.rand(n_samples, n_features)
    y = np.zeros((n_samples, n_tasks))
    dataset = dc.data.NumpyDataset(X, y)

    def input_fn(epochs):
      x, y, weights = dataset.make_iterator(
          batch_size=n_samples, epochs=epochs).get_next()
      return {'x': x, 'weights': weights}, y

    # Create a TensorGraph model.

    model = dc.models.MultitaskRegressor(n_tasks, n_features, dropouts=0)

    # Create an estimator from it.

    x_col = tf.feature_column.numeric_column('x', shape=(n_features,))
    weight_col = tf.feature_column.numeric_column('weights', shape=(n_tasks,))
    metrics = {'error': tf.metrics.mean_absolute_error}
    estimator = model.make_estimator(
        feature_columns=[x_col], weight_column=weight_col, metrics=metrics)

    # Train the model.

    estimator.train(input_fn=lambda: input_fn(100))

    # Evaluate the model.

    results = estimator.evaluate(input_fn=lambda: input_fn(1))
    assert results['loss'] < 1e-3
    assert results['error'] < 0.1

  def test_robust_multi_task_classifier(self):
    """Test creating an Estimator from a MultitaskClassifier."""
    n_samples = 10
    n_features = 3
    n_tasks = 2

    # Create a dataset and an input function for processing it.

    np.random.seed(123)
    X = np.random.rand(n_samples, n_features)
    y = np.zeros((n_samples, n_tasks))
    dataset = dc.data.NumpyDataset(X, y)

    def input_fn(epochs):
      x, y, weights = dataset.make_iterator(
          batch_size=n_samples, epochs=epochs).get_next()
      return {'x': x, 'weights': weights}, y

    # Create a TensorGraph model.

    model = dc.models.RobustMultitaskClassifier(
        n_tasks,
        n_features,
        layer_sizes=[50],
        bypass_layer_sizes=[10],
        dropouts=0,
        bypass_dropouts=0,
        learning_rate=0.003)

    # Create an estimator from it.

    x_col = tf.feature_column.numeric_column('x', shape=(n_features,))
    weight_col = tf.feature_column.numeric_column('weights', shape=(n_tasks,))

    def accuracy(labels, predictions, weights):
      return tf.metrics.accuracy(labels, tf.round(predictions), weights)

    metrics = {'accuracy': accuracy}
    estimator = model.make_estimator(
        feature_columns=[x_col], weight_column=weight_col, metrics=metrics)

    # Train the model.

    estimator.train(input_fn=lambda: input_fn(500))

    # Evaluate the model.

    results = estimator.evaluate(input_fn=lambda: input_fn(1))
    assert results['loss'] < 1e-2
    assert results['accuracy'] > 0.9

  def test_robust_multi_task_regressor(self):
    """Test creating an Estimator from a MultitaskRegressor."""
    n_samples = 10
    n_features = 3
    n_tasks = 2

    # Create a dataset and an input function for processing it.

    np.random.seed(123)
    X = np.random.rand(n_samples, n_features)
    y = np.zeros((n_samples, n_tasks))
    dataset = dc.data.NumpyDataset(X, y)

    def input_fn(epochs):
      x, y, weights = dataset.make_iterator(
          batch_size=n_samples, epochs=epochs).get_next()
      return {'x': x, 'weights': weights}, y

    # Create a TensorGraph model.

    model = dc.models.RobustMultitaskRegressor(
        n_tasks,
        n_features,
        layer_sizes=[50],
        bypass_layer_sizes=[10],
        dropouts=0,
        bypass_dropouts=0,
        learning_rate=0.003)

    # Create an estimator from it.

    x_col = tf.feature_column.numeric_column('x', shape=(n_features,))
    weight_col = tf.feature_column.numeric_column('weights', shape=(n_tasks,))
    metrics = {'error': tf.metrics.mean_absolute_error}
    estimator = model.make_estimator(
        feature_columns=[x_col], weight_column=weight_col, metrics=metrics)

    # Train the model.

    estimator.train(input_fn=lambda: input_fn(500))

    # Evaluate the model.

    results = estimator.evaluate(input_fn=lambda: input_fn(1))
    assert results['loss'] < 1e-2
    assert results['error'] < 1e-2

  def test_sequential(self):
    """Test creating an Estimator from a Sequential model."""
    n_samples = 20
    n_features = 2

    # Create a dataset and an input function for processing it.

    X = np.random.rand(n_samples, n_features)
    y = np.array([[0.5] for x in range(n_samples)])
    dataset = dc.data.NumpyDataset(X, y)

    def input_fn(epochs):
      x, y, weights = dataset.make_iterator(
          batch_size=n_samples, epochs=epochs).get_next()
      return {'x': x}, y

    # Create the model.

    model = dc.models.Sequential(loss="mse", learning_rate=0.01)
    model.add(layers.Dense(out_channels=1))

    # Create an estimator from it.

    x_col = tf.feature_column.numeric_column('x', shape=(n_features,))
    metrics = {'error': tf.metrics.mean_absolute_error}
    estimator = model.make_estimator(feature_columns=[x_col], metrics=metrics)

    # Train the model.

    estimator.train(input_fn=lambda: input_fn(1000))

    # Evaluate the model.

    results = estimator.evaluate(input_fn=lambda: input_fn(1))
    assert results['loss'] < 1e-2
    assert results['error'] < 0.1

  def test_irv(self):
    """Test creating an Estimator from a IRVClassifier."""
    n_samples = 50
    n_features = 3
    n_tasks = 2

    # Create a dataset and an input function for processing it.

    np.random.seed(123)
    X = np.random.rand(n_samples, n_features)
    y = np.zeros((n_samples, n_tasks))
    dataset = dc.data.NumpyDataset(X, y)
    transformers = [dc.trans.IRVTransformer(10, n_tasks, dataset)]

    for transformer in transformers:
      dataset = transformer.transform(dataset)

    def input_fn(epochs):
      x, y, weights = dataset.make_iterator(
          batch_size=n_samples, epochs=epochs).get_next()
      return {'x': x, 'weights': weights}, y

    # Create a TensorGraph model.

    model = dc.models.TensorflowMultitaskIRVClassifier(
        n_tasks, K=10, learning_rate=0.001, penalty=0.05, batch_size=50)
    model.build()
    # Create an estimator from it.

    x_col = tf.feature_column.numeric_column('x', shape=(2 * 10 * n_tasks,))
    weight_col = tf.feature_column.numeric_column('weights', shape=(n_tasks,))

    def accuracy(labels, predictions, weights):
      return tf.metrics.accuracy(labels, tf.round(predictions[:, :, 1]),
                                 weights)

    metrics = {'accuracy': accuracy}
    estimator = model.make_estimator(
        feature_columns=[x_col], weight_column=weight_col, metrics=metrics)

    # Train the model.

    estimator.train(input_fn=lambda: input_fn(100))

    # Evaluate the model.

    results = estimator.evaluate(input_fn=lambda: input_fn(1))
    assert results['accuracy'] > 0.9

  def test_textcnn_classification(self):
    """Test creating an Estimator from TextCNN for classification."""
    n_tasks = 2
    n_samples = 5

    # Create a TensorGraph model.
    seq_length = 20
    model = dc.models.TextCNNModel(
        n_tasks=n_tasks,
        char_dict=default_dict,
        seq_length=seq_length,
        kernel_sizes=[5, 5],
        num_filters=[20, 20])

    np.random.seed(123)
    smile_ids = ["CCCCC", "CCC(=O)O", "CCC", "CC(=O)O", "O=C=O"]
    X = [model.smiles_to_seq(smile) for smile in smile_ids]
    y = np.zeros((n_samples, n_tasks))
    w = np.ones((n_samples, n_tasks))
    dataset = NumpyDataset(X, y, w, smile_ids)

    def accuracy(labels, predictions, weights):
      return tf.metrics.accuracy(labels, tf.round(predictions), weights)

    def input_fn(epochs):
      x, y, weights = dataset.make_iterator(
          batch_size=n_samples, epochs=epochs).get_next()
      return {'x': x, 'weights': weights}, y

    # Create an estimator from it.
    x_col = tf.feature_column.numeric_column(
        'x', shape=(seq_length,), dtype=tf.int32)
    weight_col = tf.feature_column.numeric_column('weights', shape=(n_tasks,))
    metrics = {'accuracy': accuracy}
    estimator = model.make_estimator(
        feature_columns=[x_col], weight_column=weight_col, metrics=metrics)

    # Train the model.
    estimator.train(input_fn=lambda: input_fn(100))

    # Evaluate results
    results = estimator.evaluate(input_fn=lambda: input_fn(1))
    assert results['loss'] < 1e-2
    assert results['accuracy'] > 0.9

  def test_textcnn_regression(self):
    """Test creating an Estimator from TextCNN for regression."""
    n_tasks = 2
    n_samples = 10

    # Create a TensorGraph model.
    seq_length = 20
    model = dc.models.TextCNNModel(
        n_tasks=n_tasks,
        char_dict=default_dict,
        seq_length=seq_length,
        kernel_sizes=[5, 5],
        num_filters=[20, 20],
        mode="regression")

    np.random.seed(123)
    smile_ids = ["CCCCC", "CCC(=O)O", "CCC", "CC(=O)O", "O=C=O"]
    X = [model.smiles_to_seq(smile) for smile in smile_ids]
    y = np.zeros((n_samples, n_tasks, 1), dtype=np.float32)
    w = np.ones((n_samples, n_tasks))
    dataset = NumpyDataset(X, y, w, smile_ids)

    def input_fn(epochs):
      x, y, weights = dataset.make_iterator(
          batch_size=n_samples, epochs=epochs).get_next()
      return {'x': x, 'weights': weights}, y

    # Create an estimator from it.
    x_col = tf.feature_column.numeric_column('x', shape=(seq_length,))
    weight_col = tf.feature_column.numeric_column('weights', shape=(n_tasks,))
    metrics = {'error': tf.metrics.mean_absolute_error}
    estimator = model.make_estimator(
        feature_columns=[x_col], weight_column=weight_col, metrics=metrics)

    # Train the model.
    estimator.train(input_fn=lambda: input_fn(100))
    results = estimator.evaluate(input_fn=lambda: input_fn(1))
    assert results['loss'] < 1e-1
    assert results['error'] < 0.1

  def test_scscore(self):
    """Test creating an Estimator from a ScScoreModel."""
    n_samples = 10
    n_features = 3
    n_tasks = 1

    # Create a dataset and an input function for processing it.

    np.random.seed(123)
    X = np.random.rand(n_samples, 2, n_features)
    y = np.zeros((n_samples, n_tasks))
    dataset = dc.data.NumpyDataset(X, y)

    def input_fn(epochs):
      x, y, weights = dataset.make_iterator(
          batch_size=n_samples, epochs=epochs).get_next()
      x1 = x[:, 0]
      x2 = x[:, 1]
      return {'x1': x1, 'x2': x2, 'weights': weights}, y

    # Create a TensorGraph model.

    model = dc.models.ScScoreModel(n_features, dropouts=0)
    del model.outputs[:]
    model.outputs.append(model.difference)

    def accuracy(labels, predictions, weights):
      predictions = tf.nn.relu(tf.sign(predictions))
      return tf.metrics.accuracy(labels, predictions, weights)

    # Create an estimator from it.

    x_col1 = tf.feature_column.numeric_column('x1', shape=(n_features,))
    x_col2 = tf.feature_column.numeric_column('x2', shape=(n_features,))
    weight_col = tf.feature_column.numeric_column('weights', shape=(1,))

    estimator = model.make_estimator(
        feature_columns=[x_col1, x_col2],
        metrics={'accuracy': accuracy},
        weight_column=weight_col)

    # Train the model.

    estimator.train(input_fn=lambda: input_fn(100))

    # Evaluate the model.

    results = estimator.evaluate(input_fn=lambda: input_fn(1))
    assert results['loss'] < 0.5
    assert results['accuracy'] > 0.6

  def test_tensorboard(self):
    """Test creating an Estimator from a TensorGraph that logs information to TensorBoard."""
    n_samples = 10
    n_features = 3
    n_tasks = 2

    # Create a dataset and an input function for processing it.

    np.random.seed(123)
    X = np.random.rand(n_samples, n_features)
    y = np.zeros((n_samples, n_tasks))
    dataset = dc.data.NumpyDataset(X, y)

    def input_fn(epochs):
      x, y, weights = dataset.make_iterator(
          batch_size=n_samples, epochs=epochs).get_next()
      return {'x': x, 'weights': weights}, y

    # Create a TensorGraph model.

    model = dc.models.TensorGraph()
    features = layers.Feature(shape=(None, n_features))
    dense = layers.Dense(out_channels=n_tasks, in_layers=features)
    dense.set_summary('histogram')
    model.add_output(dense)
    labels = layers.Label(shape=(None, n_tasks))
    loss = layers.ReduceMean(layers.L2Loss(in_layers=[labels, dense]))
    model.set_loss(loss)

    # Create an estimator from it.

    x_col = tf.feature_column.numeric_column('x', shape=(n_features,))
    estimator = model.make_estimator(feature_columns=[x_col])

    # Train the model.

    estimator.train(input_fn=lambda: input_fn(100))
