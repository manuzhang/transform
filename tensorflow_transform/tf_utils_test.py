# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for tensorflow_transform.tf_utils."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# GOOGLE-INITIALIZATION
import numpy as np
import tensorflow as tf

from tensorflow_transform import tf_utils
from tensorflow_transform import test_case


class AnalyzersTest(test_case.TransformTestCase):

  @test_case.named_parameters(
      dict(
          testcase_name='rank1',
          x=['a', 'b', 'a'],
          weights=None,
          expected_results=[[b'a', b'b', b'a']]),
      dict(
          testcase_name='rank1_with_weights',
          x=['a', 'b', 'a'],
          weights=[1, 1, 2],
          expected_results=[[b'a', b'b'], [3, 1]]),
      dict(
          testcase_name='rank2',
          x=[['a', 'b', 'a'], ['b', 'a', 'b']],
          weights=None,
          expected_results=[[b'a', b'b', b'a', b'b', b'a', b'b']]),
      dict(
          testcase_name='rank2_with_weights',
          x=[['a', 'b', 'a'], ['b', 'a', 'b']],
          weights=[[1, 2, 1], [1, 2, 2]],
          expected_results=[[b'a', b'b'], [4, 5]]),
      dict(
          testcase_name='rank3',
          x=[[['a', 'b', 'a'], ['b', 'a', 'b']],
             [['a', 'b', 'a'], ['b', 'a', 'b']]],
          weights=None,
          expected_results=[[
              b'a', b'b', b'a', b'b', b'a', b'b', b'a', b'b', b'a', b'b', b'a',
              b'b'
          ]]),
      dict(
          testcase_name='rank3_with_weights',
          x=[[['a', 'b', 'a'], ['b', 'a', 'b']],
             [['a', 'b', 'a'], ['b', 'a', 'b']]],
          weights=[[[1, 1, 2], [1, 2, 1]], [[1, 2, 1], [1, 2, 1]]],
          expected_results=[[b'a', b'b'], [9, 7]]),
  )
  def test_reduce_batch_weighted_counts(self, x, weights, expected_results):
    x = tf.constant(x)
    if weights is not None:
      weights = tf.constant(weights)

    returned_tensors = tf_utils.reduce_batch_weighted_counts(x, weights)
    with tf.compat.v1.Session() as sess:
      results = sess.run([a for a in returned_tensors if a is not None])
      for result, expected in zip(results, expected_results):
        self.assertAllEqual(result, np.array(expected))

  @test_case.named_parameters(
      dict(
          testcase_name='rank1_with_binary_y',
          x=['a', 'b', 'a'],
          weights=None,
          y=[0, 1, 1],
          expected_results=[[b'a', b'b', b'global_y_count_sentinel'], [2, 1, 3],
                            [[1, 1], [0, 1], [1, 2]], [2, 1, 3]]),
      dict(
          testcase_name='rank1_with_multi_class_y',
          x=['yes', 'no', 'yes', 'maybe', 'yes'],
          weights=None,
          y=[1, 1, 0, 2, 3],
          expected_results=[[
              b'yes', b'no', b'maybe', b'global_y_count_sentinel'
          ], [3, 1, 1, 5],
                            [[1, 1, 0, 1], [0, 1, 0, 0], [0, 0, 1, 0],
                             [1, 2, 1, 1]], [3, 1, 1, 5]]),
      dict(
          testcase_name='rank1_with_weights_and_binary_y',
          x=['a', 'b', 'a'],
          weights=[1, 1, 2],
          y=[0, 1, 1],
          expected_results=[[b'a', b'b', b'global_y_count_sentinel'], [3, 1, 4],
                            [[1, 2], [0, 1], [1, 3]], [2, 1, 3]]),
      dict(
          testcase_name='rank1_with_weights_and_multi_class_y',
          x=['a', 'b', 'a', 'a'],
          weights=[1, 1, 2, 2],
          y=[0, 2, 1, 1],
          expected_results=[[b'a', b'b', b'global_y_count_sentinel'], [5, 1, 6],
                            [[1, 4, 0], [0, 0, 1], [1, 4, 1]], [3, 1, 4]]),
      dict(
          testcase_name='rank1_with_weights_and_missing_y_values',
          x=['a', 'b', 'a', 'a'],
          weights=[1, 1, 2, 2],
          y=[3, 5, 6, 6],
          expected_results=[[b'a', b'b', b'global_y_count_sentinel'], [5, 1, 6],
                            [[0, 0, 0, 1, 0, 0, 4], [0, 0, 0, 0, 0, 1, 0],
                             [0, 0, 0, 1, 0, 1, 4]], [3, 1, 4]]),
      dict(
          testcase_name='rank2_with_binary_y',
          x=[['a', 'b', 'a'], ['b', 'a', 'b']],
          weights=None,
          y=[[1, 0, 1], [1, 0, 0]],
          expected_results=[[b'a', b'b', b'global_y_count_sentinel'], [3, 3, 6],
                            [[1, 2], [2, 1], [3, 3]], [3, 3, 6]]),
      dict(
          testcase_name='rank2_with_missing_y_values',
          x=[['a', 'b', 'a'], ['b', 'a', 'b']],
          weights=None,
          y=[[2, 0, 2], [2, 0, 0]],
          # The label 1 isn't in the batch but it will have a position (with
          # weights of 0) in the resulting array.
          expected_results=[[b'a', b'b', b'global_y_count_sentinel'], [3, 3, 6],
                            [[1, 0, 2], [2, 0, 1], [3, 0, 3]], [3, 3, 6]]),
      dict(
          testcase_name='rank2_with_weights_and_binary_y',
          x=[['a', 'b', 'a'], ['b', 'a', 'b']],
          weights=[[1, 2, 1], [1, 2, 2]],
          y=[[1, 0, 1], [1, 0, 0]],
          expected_results=[[b'a', b'b', b'global_y_count_sentinel'], [4, 5, 9],
                            [[2, 2], [4, 1], [6, 3]], [3, 3, 6]]),
      dict(
          testcase_name='rank2_with_multi_class_y',
          x=[['a', 'b', 'a'], ['b', 'a', 'b']],
          weights=None,
          y=[[1, 0, 1], [1, 0, 2]],
          expected_results=[[b'a', b'b', b'global_y_count_sentinel'], [3, 3, 6],
                            [[1, 2, 0], [1, 1, 1], [2, 3, 1]], [3, 3, 6]]),
      dict(
          testcase_name='rank3_with_binary_y',
          x=[[['a', 'b', 'a'], ['b', 'a', 'b']],
             [['a', 'b', 'a'], ['b', 'a', 'b']]],
          weights=None,
          y=[[[1, 1, 0], [1, 0, 1]], [[1, 0, 1], [1, 0, 1]]],
          expected_results=[[b'a', b'b', b'global_y_count_sentinel'],
                            [6, 6, 12], [[3, 3], [1, 5], [4, 8]], [6, 6, 12]]),
      dict(
          testcase_name='rank3_with_weights_and_binary_y',
          x=[[['a', 'b', 'a'], ['b', 'a', 'b']],
             [['a', 'b', 'a'], ['b', 'a', 'b']]],
          weights=[[[1, 1, 2], [1, 2, 1]], [[1, 2, 1], [1, 2, 1]]],
          y=[[[1, 1, 0], [1, 0, 1]], [[1, 0, 1], [1, 0, 1]]],
          expected_results=[[b'a', b'b', b'global_y_count_sentinel'],
                            [9, 7, 16], [[6, 3], [2, 5], [8, 8]], [6, 6, 12]]),
  )
  def test_reduce_batch_coocurrences(self, x, weights, y, expected_results):
    x = tf.constant(x)
    y = tf.constant(y, dtype=tf.int64)
    if weights is not None:
      weights = tf.constant(weights)

    returned_tensors = (
        tf_utils.reduce_batch_weighted_cooccurrences(x, y, weights))
    with tf.compat.v1.Session() as sess:
      results = sess.run(returned_tensors)
      for result, expected in zip(results, expected_results):
        self.assertAllEqual(result, np.array(expected))

  def test_reduce_batch_coocurrences_sparse_tensor(self):
    x = tf.SparseTensor(
        indices=[(0, 0), (2, 1)], values=['a', 'b'], dense_shape=[4, 2])
    y = tf.constant([0, 1, 0, 0], dtype=tf.int64)
    expected_results = [[b'a', b'b', b'global_y_count_sentinel'], [1, 1, 4],
                        [[1, 0], [1, 0], [3, 1]], [1, 1, 4]]
    returned_tensors = (
        tf_utils.reduce_batch_weighted_cooccurrences(x, y, None))
    with tf.compat.v1.Session() as sess:
      results = sess.run(returned_tensors)
      for result, expected in zip(results, expected_results):
        self.assertAllEqual(result, np.array(expected))

  def test_reduce_batch_coocurrences_empty_sparse_tensor(self):
    x = tf.SparseTensor(
        indices=tf.constant([], shape=(0, 2), dtype=tf.int64),
        values=tf.constant([], shape=(0,), dtype=tf.string),
        dense_shape=[4, 2])
    y = tf.constant([1, 0, 1, 1], dtype=tf.int64)
    expected_results = [[b'global_y_count_sentinel'], [4], [[1, 3]], [4]]
    returned_tensors = (
        tf_utils.reduce_batch_weighted_cooccurrences(x, y, None))
    with tf.compat.v1.Session() as sess:
      results = sess.run(returned_tensors)
      for result, expected in zip(results, expected_results):
        self.assertAllEqual(result, np.array(expected))

  @test_case.parameters(
      ([[1], [2]], [[1], [2], [3]], None, None, tf.errors.InvalidArgumentError,
       'Condition x == y did not hold element-wise:'),
      ([[1], [2], [3]], [[1], [2], [3]], [None, None], [None], ValueError,
       r'Shapes \(None, None\) and \(None,\) are incompatible'),
  )
  def test_same_shape_exceptions(self, x_input, y_input, x_shape, y_shape,
                                 exception_cls, error_string):
    x = tf.compat.v1.placeholder(tf.int32, shape=x_shape)
    y = tf.compat.v1.placeholder(tf.int32, shape=y_shape)
    with tf.compat.v1.Session() as sess:
      with self.assertRaisesRegexp(exception_cls, error_string):
        sess.run(tf_utils.assert_same_shape(x, y), {x: x_input, y: y_input})

  def test_same_shape(self):
    with tf.compat.v1.Session() as sess:
      input_list = [[1], [2], [3]]
      x = tf.compat.v1.placeholder(tf.int32, shape=None)
      y = tf.compat.v1.placeholder(tf.int32, shape=None)
      x_return = sess.run(
          tf_utils.assert_same_shape(x, y), {
              x: input_list,
              y: input_list
          })
      self.assertAllEqual(x_return, input_list)

  def test_reduce_batch_count(self):
    x = tf.constant([[[1], [2]], [[1], [2]]])
    with tf.compat.v1.Session():
      self.assertAllEqual(
          tf_utils.reduce_batch_count(x, reduce_instance_dims=True).eval(), 4)

  def test_reduce_batch_count_elementwise(self):
    x = tf.constant([[[1], [2]], [[1], [2]]])
    with tf.compat.v1.Session():
      self.assertAllEqual(
          tf_utils.reduce_batch_count(x, reduce_instance_dims=False).eval(),
          [[2], [2]])

  def test_reduce_batch_count_sparse(self):
    x = tf.SparseTensor(
        indices=[[0, 0, 0], [0, 2, 0], [1, 1, 0], [1, 2, 0]],
        values=[1., 2., 3., 4.],
        dense_shape=[2, 4, 1])
    with tf.compat.v1.Session():
      self.assertAllEqual(
          tf_utils.reduce_batch_count(x, reduce_instance_dims=True).eval(), 4)

  def test_reduce_batch_count_sparse_elementwise(self):
    x = tf.SparseTensor(
        indices=[[0, 0, 0], [0, 2, 0], [1, 1, 0], [1, 2, 0]],
        values=[1., 2., 3., 4.],
        dense_shape=[2, 4, 1])
    with tf.compat.v1.Session():
      self.assertAllEqual(
          tf_utils.reduce_batch_count(x, reduce_instance_dims=False).eval(),
          [[1], [1], [2], [0]])

  def test_reduce_batch_count_mean_and_var(self):
    x = tf.constant([[[1], [2]], [[3], [4]]], dtype=tf.float32)
    count, mean, var = tf_utils.reduce_batch_count_mean_and_var(
        x, reduce_instance_dims=True)
    with tf.compat.v1.Session():
      self.assertAllEqual(count.eval(), 4)
      self.assertAllEqual(mean.eval(), 2.5)
      self.assertAllEqual(var.eval(), 1.25)

  def test_reduce_batch_count_mean_and_var_elementwise(self):
    x = tf.constant([[[1], [2]], [[3], [4]]], dtype=tf.float32)
    count, mean, var = tf_utils.reduce_batch_count_mean_and_var(
        x, reduce_instance_dims=False)
    with tf.compat.v1.Session():
      self.assertAllEqual(count.eval(), [[2.], [2.]])
      self.assertAllEqual(mean.eval(), [[2.], [3.]])
      self.assertAllEqual(var.eval(), [[1.], [1.]])

  def test_reduce_batch_count_mean_and_var_sparse(self):
    x = tf.SparseTensor(
        indices=[[0, 0], [0, 2], [1, 1], [1, 2]],
        values=[1., 2., 3., 4.],
        dense_shape=[2, 4])
    count, mean, var = tf_utils.reduce_batch_count_mean_and_var(
        x, reduce_instance_dims=True)
    with tf.compat.v1.Session():
      self.assertAllEqual(count.eval(), 4)
      self.assertAllEqual(mean.eval(), 2.5)
      self.assertAllEqual(var.eval(), 1.25)

  def test_reduce_batch_count_mean_and_var_sparse_elementwise(self):
    x = tf.SparseTensor(
        indices=[[0, 0], [0, 3], [1, 1], [1, 3]],
        values=[1., 2., 3., 4.],
        dense_shape=[2, 5])
    count, mean, var = tf_utils.reduce_batch_count_mean_and_var(
        x, reduce_instance_dims=False)
    with tf.compat.v1.Session():
      self.assertAllEqual(count.eval(), [1.0, 1.0, 0.0, 2.0, 0.0])
      self.assertAllEqual(mean.eval(), [1.0, 3.0, 0.0, 3.0, 0.0])
      self.assertAllEqual(var.eval(), [0.0, 0.0, 0.0, 1.0, 0.0])

  def test_reduce_batch_count_mean_and_var_per_key(self):
    x = tf.constant([[1], [2], [3], [4], [4]], dtype=tf.float32)
    key = tf.constant(['a', 'a', 'a', 'b', 'a'], dtype=tf.string)
    key_vocab, count, mean, var = (
        tf_utils.reduce_batch_count_mean_and_var_per_key(x, key, True))
    with tf.compat.v1.Session():
      self.assertAllEqual(key_vocab.eval(), tf.constant(['a', 'b']))
      self.assertAllEqual(count.eval(), tf.constant([4, 1]))
      self.assertAllEqual(mean.eval(), tf.constant([2.5, 4]))
      self.assertAllEqual(var.eval(), tf.constant([1.25, 0]))

  def test_reduce_batch_count_mean_and_var_per_key_elementwise(self):
    x = tf.constant([[1, 2], [3, 4], [1, 2]], dtype=tf.float32)
    key = tf.constant(['a', 'a', 'b'], dtype=tf.string)
    key_vocab, count, mean, var = (
        tf_utils.reduce_batch_count_mean_and_var_per_key(x, key, False))
    with tf.compat.v1.Session():
      self.assertAllEqual(key_vocab.eval(), tf.constant(['a', 'b']))
      self.assertAllEqual(count.eval(), [[2., 2.], [1., 1.]])
      self.assertAllEqual(mean.eval(), [[2., 3.], [1., 2.]])
      self.assertAllEqual(var.eval(), [[1., 1.], [0., 0.]])

  def test_reduce_batch_count_mean_and_var_per_key_sparse(self):
    x = tf.SparseTensor(
        indices=[[0, 0], [0, 2], [1, 1], [1, 2], [2, 3]],
        values=[1., 2., 3., 4., 4.],
        dense_shape=[3, 4])
    key = tf.SparseTensor(
        indices=[[0, 0], [0, 2], [1, 1], [1, 2], [2, 3]],
        values=['a', 'a', 'a', 'a', 'b'],
        dense_shape=[3, 4])
    key_vocab, count, mean, var = (
        tf_utils.reduce_batch_count_mean_and_var_per_key(x, key, True))
    with tf.compat.v1.Session():
      self.assertAllEqual(key_vocab.eval(), tf.constant(['a', 'b']))
      self.assertAllEqual(count.eval(), tf.constant([4, 1]))
      self.assertAllEqual(mean.eval(), tf.constant([2.5, 4]))
      self.assertAllEqual(var.eval(), tf.constant([1.25, 0]))

  # pylint: disable=g-long-lambda
  @test_case.named_parameters(
      dict(
          testcase_name='sparse',
          placeholder_fn=lambda: tf.compat.v1.sparse_placeholder(
              tf.int64, [None, None]),
          value=tf.compat.v1.SparseTensorValue(
              indices=[[0, 0], [0, 1], [0, 2]],
              values=[3, 2, -1],
              dense_shape=[1, 5]),
          reduce_instance_dims=True,
          expected_result=(1, 3)),
      dict(
          testcase_name='float',
          placeholder_fn=lambda: tf.compat.v1.placeholder(
              tf.float32, [None, None]),
          value=[[1, 5, 2]],
          reduce_instance_dims=True,
          expected_result=(-1, 5)),
      dict(
          testcase_name='sparse_float_elementwise',
          placeholder_fn=lambda: tf.compat.v1.sparse_placeholder(
              tf.float32, [None, None]),
          value=tf.compat.v1.SparseTensorValue(
              indices=[[0, 0], [0, 1], [1, 0]],
              values=[3, 2, -1],
              dense_shape=[2, 3]),
          reduce_instance_dims=False,
          expected_result=([[1, -2, np.nan], [3, 2, np.nan]])),
      dict(
          testcase_name='float_elementwise',
          placeholder_fn=lambda: tf.compat.v1.placeholder(
              tf.float32, [None, None]),
          value=[[1, 5, 2], [2, 3, 4]],
          reduce_instance_dims=False,
          expected_result=([[-1, -3, -2], [2, 5, 4]])),
      dict(
          testcase_name='sparse_int64_elementwise',
          placeholder_fn=lambda: tf.compat.v1.sparse_placeholder(
              tf.int64, [None, None]),
          value=tf.compat.v1.SparseTensorValue(
              indices=[[0, 0], [0, 1], [1, 0]],
              values=[3, 2, -1],
              dense_shape=[2, 3]),
          reduce_instance_dims=False,
          expected_result=([[1, -2, tf.int64.min + 1], [3, 2,
                                                        tf.int64.min + 1]])),
      dict(
          testcase_name='sparse_int32_elementwise',
          placeholder_fn=lambda: tf.compat.v1.sparse_placeholder(
              tf.int32, [None, None]),
          value=tf.compat.v1.SparseTensorValue(
              indices=[[0, 0], [0, 1], [1, 0]],
              values=[3, 2, -1],
              dense_shape=[2, 3]),
          reduce_instance_dims=False,
          expected_result=([[1, -2, tf.int32.min + 1], [3, 2,
                                                        tf.int32.min + 1]])),
      dict(
          testcase_name='sparse_float32_elementwise',
          placeholder_fn=lambda: tf.compat.v1.sparse_placeholder(
              tf.float32, [None, None]),
          value=tf.compat.v1.SparseTensorValue(
              indices=[[0, 0], [0, 1], [1, 0]],
              values=[3, 2, -1],
              dense_shape=[2, 3]),
          reduce_instance_dims=False,
          expected_result=([[1, -2, np.nan], [3, 2, np.nan]])),
      dict(
          testcase_name='sparse_float64_elementwise',
          placeholder_fn=lambda: tf.compat.v1.sparse_placeholder(
              tf.float64, [None, None]),
          value=tf.compat.v1.SparseTensorValue(
              indices=[[0, 0], [0, 1], [1, 0]],
              values=[3, 2, -1],
              dense_shape=[2, 3]),
          reduce_instance_dims=False,
          expected_result=([[1, -2, np.nan], [3, 2, np.nan]])),
  )
  # pylint: enable=g-long-lambda
  def test_reduce_batch_minus_min_and_max(self, placeholder_fn, value,
                                          reduce_instance_dims,
                                          expected_result):
    x = placeholder_fn()
    batch_minus_min, batch_max = tf_utils.reduce_batch_minus_min_and_max(
        x, reduce_instance_dims)

    with tf.compat.v1.Session() as sess:
      result = sess.run([batch_minus_min, batch_max], feed_dict={x: value})
    self.assertAllEqual(result, expected_result)

  # pylint: disable=g-long-lambda
  @test_case.named_parameters(
      dict(
          testcase_name='sparse',
          placeholder_fn=lambda: tf.compat.v1.sparse_placeholder(
              tf.int64, [None, None]),
          value=tf.compat.v1.SparseTensorValue(
              indices=[[0, 0], [1, 1], [2, 2], [3, 1]],
              values=[3, 2, -1, 3],
              dense_shape=[4, 5]),
          expected_result=(np.array([b'a', b'b'], np.object), [1, -3], [3, 3])),
      dict(
          testcase_name='float',
          placeholder_fn=lambda: tf.compat.v1.placeholder(
              tf.float32, [None, None]),
          value=[[1], [5], [2], [3]],
          expected_result=(np.array([b'a', b'b'], np.object), [-1, -3], [5,
                                                                         3])),
      dict(
          testcase_name='float3dims',
          placeholder_fn=lambda: tf.compat.v1.placeholder(
              tf.float32, [None, None, None]),
          value=[[[1, 5], [1, 1]], [[5, 1], [5, 5]], [[2, 2], [2, 5]],
                 [[3, -3], [3, 3]]],
          expected_result=(np.array([b'a', b'b'], np.object), [-1, 3], [5, 3])))
  # pylint: enable=g-long-lambda
  def test_reduce_batch_minus_min_and_max_per_key(self, placeholder_fn, value,
                                                  expected_result):
    x = placeholder_fn()
    key = tf.constant(['a', 'a', 'a', 'b'])
    batch_keys, batch_minus_min, batch_max = (
        tf_utils.reduce_batch_minus_min_and_max_per_key(x, key))
    with tf.compat.v1.Session() as sess:
      result = sess.run([batch_keys, batch_minus_min, batch_max],
                        feed_dict={x: value})
    self.assertAllEqual(result[0], expected_result[0])
    self.assertAllEqual(result[1:], expected_result[1:])

  @test_case.named_parameters(
      dict(
          testcase_name='sparse_tensor',
          feature=tf.compat.v1.SparseTensorValue(
              indices=[[0, 0], [0, 1], [0, 2], [1, 0]],
              values=[1., 2., 3., 4.],
              dense_shape=[2, 5]),
          ascii_protos=[
              'float_list { value: [1.0, 2.0, 3.0] }',
              'float_list { value: [4.0] }',
          ]),
      dict(
          testcase_name='dense_scalar_int',
          feature=np.array([0, 1, 2], np.int64),
          ascii_protos=[
              'int64_list { value: [0] }',
              'int64_list { value: [1] }',
              'int64_list { value: [2] }',
          ]),
      dict(
          testcase_name='dense_scalar_float',
          feature=np.array([0.5, 1.5, 2.5], np.float32),
          ascii_protos=[
              'float_list { value: [0.5] }',
              'float_list { value: [1.5] }',
              'float_list { value: [2.5] }',
          ]),
      dict(
          testcase_name='dense_scalar_string',
          feature=np.array(['hello', 'world'], np.object),
          ascii_protos=[
              'bytes_list { value: "hello" }',
              'bytes_list { value: "world" }',
          ]),
      dict(
          testcase_name='dense_vector_int',
          feature=np.array([[0, 1], [2, 3]], np.int64),
          ascii_protos=[
              'int64_list { value: [0, 1] }',
              'int64_list { value: [2, 3] }',
          ]),
      dict(
          testcase_name='dense_matrix_int',
          feature=np.array([[[0, 1], [2, 3]], [[4, 5], [6, 7]]], np.int64),
          ascii_protos=[
              'int64_list { value: [0, 1, 2, 3] }',
              'int64_list { value: [4, 5, 6, 7] }',
          ]),
  )
  def test_serialize_feature(self, feature, ascii_protos):
    serialized_features_tensor = tf_utils._serialize_feature(feature)
    with tf.compat.v1.Session():
      serialized_features = serialized_features_tensor.eval()
      feature_proto = tf.train.Feature()
    self.assertEqual(len(serialized_features), len(ascii_protos))
    for ascii_proto, serialized_feature in zip(ascii_protos,
                                               serialized_features):
      feature_proto.ParseFromString(serialized_feature)
      self.assertProtoEquals(ascii_proto, feature_proto)

  @test_case.named_parameters(
      dict(
          testcase_name='multiple_features',
          examples={
              'my_value':
                  tf.compat.v1.SparseTensorValue(
                      indices=[[0, 0], [0, 1], [0, 2], [1, 0]],
                      values=[1., 2., 3., 4.],
                      dense_shape=[2, 5]),
              'my_other_value':
                  np.array([1, 2], np.int64),
          },
          ascii_protos=[
              """
               features {
                 feature {
                   key: "my_value"
                   value: { float_list { value: [1, 2, 3] } }
                 }
                 feature {
                   key: "my_other_value"
                    value: { int64_list { value: [1] } }
                 }
               }
               """, """
               features {
                 feature {
                   key: "my_value"
                   value: { float_list { value: [4] } }
                 }
                 feature {
                   key: "my_other_value"
                    value: { int64_list { value: [2] } }
                 }
               }
               """
          ]))
  def test_serialize_example(self, examples, ascii_protos):
    serialized_examples_tensor = tf_utils.serialize_example(examples)
    with tf.compat.v1.Session():
      serialized_examples = serialized_examples_tensor.eval()
      example_proto = tf.train.Example()
    self.assertEqual(len(serialized_examples), len(ascii_protos))
    for ascii_proto, serialized_example in zip(ascii_protos,
                                               serialized_examples):
      example_proto.ParseFromString(serialized_example)
      self.assertProtoEquals(ascii_proto, example_proto)

  def test_extend_reduced_batch_with_y_counts(self):
    initial_reduction = tf_utils.ReducedBatchWeightedCounts(
        unique_x=tf.constant(['foo', 'bar']),
        summed_weights_per_x=tf.constant([2.0, 4.0]),
        summed_positive_per_x_and_y=tf.constant([[1.0, 3.0], [1.0, 1.0]]),
        counts_per_x=tf.constant([2, 4], dtype=tf.int64))
    y = tf.constant([0, 1, 1, 1, 0, 1, 1], tf.int64)
    extended_batch = tf_utils.extend_reduced_batch_with_y_counts(
        initial_reduction, y)
    with tf.compat.v1.Session():
      self.assertAllEqual(
          extended_batch.unique_x.eval(),
          np.array([b'foo', b'bar', b'global_y_count_sentinel']))
      self.assertAllClose(extended_batch.summed_weights_per_x.eval(),
                          np.array([2.0, 4.0, 7.0]))
      self.assertAllClose(extended_batch.summed_positive_per_x_and_y.eval(),
                          np.array([[1.0, 3.0], [1.0, 1.0], [2.0, 5.0]]))
      self.assertAllClose(extended_batch.counts_per_x.eval(),
                          np.array([2.0, 4.0, 7.0]))


if __name__ == '__main__':
  # TODO(b/133440043): Remove this once TFT supports eager execution.
  tf.compat.v1.disable_eager_execution()
  # TODO(b/133440043): Remove this once this is enabled by default.
  tf.compat.v1.enable_v2_tensorshape()
  test_case.main()
