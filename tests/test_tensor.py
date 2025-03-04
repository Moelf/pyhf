from sys import platform
import pytest
import logging
import numpy as np
import tensorflow as tf
import pyhf
from pyhf.simplemodels import uncorrelated_background


def test_astensor_dtype(backend, caplog):
    tb = pyhf.tensorlib
    with caplog.at_level(logging.INFO, 'pyhf.tensor'):
        with pytest.raises(KeyError):
            assert tb.astensor([1, 2, 3], dtype='long')
            assert 'Invalid dtype' in caplog.text


def test_ones_dtype(backend, caplog):
    with caplog.at_level(logging.INFO, "pyhf.tensor"):
        with pytest.raises(KeyError):
            assert pyhf.tensorlib.ones([1, 2, 3], dtype="long")
            assert "Invalid dtype" in caplog.text


def test_zeros_dtype(backend, caplog):
    with caplog.at_level(logging.INFO, "pyhf.tensor"):
        with pytest.raises(KeyError):
            assert pyhf.tensorlib.zeros([1, 2, 3], dtype="long")
            assert "Invalid dtype" in caplog.text


def test_simple_tensor_ops(backend):
    tb = pyhf.tensorlib
    assert tb.tolist(tb.astensor([1, 2, 3]) + tb.astensor([4, 5, 6])) == [5, 7, 9]
    assert tb.tolist(tb.astensor([1]) + tb.astensor([4, 5, 6])) == [5, 6, 7]
    assert tb.tolist(tb.astensor([1, 2, 3]) - tb.astensor([4, 5, 6])) == [-3, -3, -3]
    assert tb.tolist(tb.astensor([4, 5, 6]) - tb.astensor([1])) == [3, 4, 5]
    assert tb.tolist(tb.sum(tb.astensor([[1, 2, 3], [4, 5, 6]]), axis=0)) == [5, 7, 9]
    assert tb.tolist(tb.product(tb.astensor([[1, 2, 3], [4, 5, 6]]), axis=0)) == [
        4,
        10,
        18,
    ]
    assert tb.tolist(tb.power(tb.astensor([1, 2, 3]), tb.astensor([1, 2, 3]))) == [
        1,
        4,
        27,
    ]
    assert tb.tolist(tb.divide(tb.astensor([4, 9, 16]), tb.astensor([2, 3, 4]))) == [
        2,
        3,
        4,
    ]
    assert tb.tolist(tb.sqrt(tb.astensor([4, 9, 16]))) == [2, 3, 4]
    # c.f. Issue #1759
    assert tb.tolist(tb.log(tb.exp(tb.astensor([2, 3, 4])))) == pytest.approx(
        [2, 3, 4], 1e-9
    )
    assert tb.tolist(tb.abs(tb.astensor([-1, -2]))) == [1, 2]
    assert tb.tolist(tb.erf(tb.astensor([-2.0, -1.0, 0.0, 1.0, 2.0]))) == pytest.approx(
        [
            -0.99532227,
            -0.84270079,
            0.0,
            0.84270079,
            0.99532227,
        ],
        1e-7,
    )
    assert tb.tolist(
        tb.erfinv(tb.erf(tb.astensor([-2.0, -1.0, 0.0, 1.0, 2.0])))
    ) == pytest.approx([-2.0, -1.0, 0.0, 1.0, 2.0], 1e-6)
    a = tb.astensor(1)
    b = tb.astensor(2)
    assert tb.tolist(a < b) is True
    assert tb.tolist(b < a) is False
    assert tb.tolist(a < a) is False
    assert tb.tolist(a > b) is False
    assert tb.tolist(b > a) is True
    assert tb.tolist(a > a) is False
    a = tb.astensor(4)
    b = tb.astensor(5)
    assert tb.tolist(tb.conditional((a < b), lambda: a + b, lambda: a - b)) == 9.0
    assert tb.tolist(tb.conditional((a > b), lambda: a + b, lambda: a - b)) == -1.0

    assert tb.tolist(tb.transpose(tb.astensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]))) == [
        [1.0, 4.0],
        [2.0, 5.0],
        [3.0, 6.0],
    ]


@pytest.mark.xfail(platform == "darwin", reason="c.f. Issue #1759")
@pytest.mark.only_tensorflow
def test_simple_tensor_ops_floating_point(backend):
    """
    xfail test to know if test_simple_tensor_ops stops failing for tensorflow
    on macos
    """
    tb = pyhf.tensorlib
    assert tb.tolist(tb.log(tb.exp(tb.astensor([2, 3, 4])))) == [2, 3, 4]


def test_tensor_where_scalar(backend):
    tb = pyhf.tensorlib
    assert tb.tolist(tb.where(tb.astensor([1, 0, 1], dtype="bool"), 1, 2)) == [1, 2, 1]


def test_tensor_where_tensor(backend):
    tb = pyhf.tensorlib
    assert tb.tolist(
        tb.where(
            tb.astensor([1, 0, 1], dtype="bool"),
            tb.astensor([1, 1, 1]),
            tb.astensor([2, 2, 2]),
        )
    ) == [1, 2, 1]


def test_tensor_to_numpy(backend):
    tb = pyhf.tensorlib
    array = [[1, 2, 3], [4, 5, 6]]
    assert np.array_equal(tb.to_numpy(tb.astensor(array)), np.array(array))


def test_tensor_ravel(backend):
    tb = pyhf.tensorlib
    assert (
        tb.tolist(
            tb.ravel(
                tb.astensor(
                    [
                        [1, 2, 3],
                        [4, 5, 6],
                    ]
                )
            )
        )
    ) == [1, 2, 3, 4, 5, 6]


def test_complex_tensor_ops(backend):
    tb = pyhf.tensorlib
    assert tb.tolist(tb.outer(tb.astensor([1, 2, 3]), tb.astensor([4, 5, 6]))) == [
        [4, 5, 6],
        [8, 10, 12],
        [12, 15, 18],
    ]
    assert tb.tolist(tb.stack([tb.astensor([1, 2, 3]), tb.astensor([4, 5, 6])])) == [
        [1, 2, 3],
        [4, 5, 6],
    ]
    assert tb.tolist(
        tb.stack([tb.astensor([1, 2, 3]), tb.astensor([4, 5, 6])], axis=1)
    ) == [[1, 4], [2, 5], [3, 6]]
    assert tb.tolist(
        tb.concatenate([tb.astensor([1, 2, 3]), tb.astensor([4, 5, 6])])
    ) == [1, 2, 3, 4, 5, 6]
    assert tb.tolist(tb.clip(tb.astensor([-2, -1, 0, 1, 2]), -1, 1)) == [
        -1,
        -1,
        0,
        1,
        1,
    ]


def test_ones(backend):
    tb = pyhf.tensorlib
    assert tb.tolist(tb.ones((2, 3))) == [[1, 1, 1], [1, 1, 1]]
    assert tb.tolist(tb.ones((4, 5))) == [[1.0] * 5] * 4


def test_normal(backend):
    tb = pyhf.tensorlib
    assert tb.tolist(
        tb.normal_logpdf(tb.astensor([0]), tb.astensor([0]), tb.astensor([1]))
    ) == pytest.approx([-0.9189385332046727], 1e-07)


def test_zeros(backend):
    tb = pyhf.tensorlib
    assert tb.tolist(tb.zeros((4, 5))) == [[0.0] * 5] * 4


def test_broadcasting(backend):
    tb = pyhf.tensorlib
    assert list(
        map(
            tb.tolist,
            tb.simple_broadcast(
                tb.astensor([1, 1, 1]), tb.astensor([2]), tb.astensor([3, 3, 3])
            ),
        )
    ) == [[1, 1, 1], [2, 2, 2], [3, 3, 3]]
    assert list(
        map(
            tb.tolist,
            tb.simple_broadcast(
                tb.astensor(1), tb.astensor([2, 3, 4]), tb.astensor([5, 6, 7])
            ),
        )
    ) == [[1, 1, 1], [2, 3, 4], [5, 6, 7]]
    assert list(
        map(
            tb.tolist,
            tb.simple_broadcast(
                tb.astensor([1]), tb.astensor([2, 3, 4]), tb.astensor([5, 6, 7])
            ),
        )
    ) == [[1, 1, 1], [2, 3, 4], [5, 6, 7]]
    with pytest.raises(Exception):
        tb.simple_broadcast(
            tb.astensor([1]), tb.astensor([2, 3]), tb.astensor([5, 6, 7])
        )


def test_reshape(backend):
    tb = pyhf.tensorlib
    assert tb.tolist(tb.reshape(tb.ones((1, 2, 3)), (-1,))) == [1, 1, 1, 1, 1, 1]


def test_swap(backend):
    tb = pyhf.tensorlib
    assert tb.tolist(tb.einsum('ij...->ji...', tb.astensor([[1, 2, 3]]))) == [
        [1],
        [2],
        [3],
    ]
    assert tb.tolist(tb.einsum('ij...->ji...', tb.astensor([[[1, 2, 3]]]))) == [
        [[1, 2, 3]]
    ]
    assert tb.tolist(tb.einsum('ijk...->kji...', tb.astensor([[[1, 2, 3]]]))) == [
        [[1]],
        [[2]],
        [[3]],
    ]


def test_shape(backend):
    tb = pyhf.tensorlib
    assert tb.shape(tb.ones((1, 2, 3, 4, 5))) == (1, 2, 3, 4, 5)
    assert tb.shape(tb.ones((0, 0))) == (0, 0)
    assert tb.shape(tb.astensor(1.0)) == ()
    assert tb.shape(tb.astensor([])) == (0,)
    assert tb.shape(tb.astensor([1.0])) == (1,)
    assert tb.shape(tb.astensor((1.0, 1.0))) == tb.shape(tb.astensor([1.0, 1.0]))
    assert tb.shape(tb.astensor((0.0, 0.0))) == tb.shape(tb.astensor([0.0, 0.0]))
    with pytest.raises(
        (ValueError, RuntimeError, tf.errors.InvalidArgumentError, TypeError)
    ):
        _ = tb.astensor([1, 2]) + tb.astensor([3, 4, 5])
    with pytest.raises(
        (ValueError, RuntimeError, tf.errors.InvalidArgumentError, TypeError)
    ):
        _ = tb.astensor([1, 2]) - tb.astensor([3, 4, 5])
    with pytest.raises(
        (ValueError, RuntimeError, tf.errors.InvalidArgumentError, TypeError)
    ):
        _ = tb.astensor([1, 2]) < tb.astensor([3, 4, 5])
    with pytest.raises(
        (ValueError, RuntimeError, tf.errors.InvalidArgumentError, TypeError)
    ):
        _ = tb.astensor([1, 2]) > tb.astensor([3, 4, 5])
    with pytest.raises((ValueError, RuntimeError, TypeError)):
        tb.conditional(
            (tb.astensor([1, 2]) < tb.astensor([3, 4])),
            lambda: tb.astensor(4) + tb.astensor(5),
            lambda: tb.astensor(4) - tb.astensor(5),
        )


@pytest.mark.fail_pytorch
@pytest.mark.fail_pytorch64
def test_pdf_calculations(backend):
    tb = pyhf.tensorlib
    assert tb.tolist(tb.normal_cdf(tb.astensor([0.8]))) == pytest.approx(
        [0.7881446014166034], 1e-07
    )
    assert tb.tolist(
        tb.normal_logpdf(
            tb.astensor([0, 0, 1, 1, 0, 0, 1, 1]),
            tb.astensor([0, 1, 0, 1, 0, 1, 0, 1]),
            tb.astensor([0, 0, 0, 0, 1, 1, 1, 1]),
        )
    ) == pytest.approx(
        [
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            -0.91893853,
            -1.41893853,
            -1.41893853,
            -0.91893853,
        ],
        nan_ok=True,
    )
    # Allow poisson(lambda=0) under limit Poisson(n = 0 | lambda -> 0) = 1
    assert tb.tolist(
        tb.poisson(tb.astensor([0, 0, 1, 1]), tb.astensor([0, 1, 0, 1]))
    ) == pytest.approx([1.0, 0.3678794503211975, 0.0, 0.3678794503211975])
    assert tb.tolist(
        tb.poisson_logpdf(tb.astensor([0, 0, 1, 1]), tb.astensor([0, 1, 0, 1]))
    ) == pytest.approx(
        np.log([1.0, 0.3678794503211975, 0.0, 0.3678794503211975]).tolist()
    )

    # Ensure continuous approximation is valid
    assert tb.tolist(
        tb.poisson(n=tb.astensor([0.5, 1.1, 1.5]), lam=tb.astensor(1.0))
    ) == pytest.approx([0.4151074974205947, 0.3515379040027489, 0.2767383316137298])


# validate_args in torch.distributions raises ValueError not nan
@pytest.mark.only_pytorch
@pytest.mark.only_pytorch64
def test_pdf_calculations_pytorch(backend):
    tb = pyhf.tensorlib

    values = tb.astensor([0, 0, 1, 1])
    mus = tb.astensor([0, 1, 0, 1])
    sigmas = tb.astensor([0, 0, 0, 0])
    for x, mu, sigma in zip(values, mus, sigmas):
        with pytest.raises(ValueError):
            _ = tb.normal_logpdf(x, mu, sigma)
    assert tb.tolist(
        tb.normal_logpdf(
            tb.astensor([0, 0, 1, 1]),
            tb.astensor([0, 1, 0, 1]),
            tb.astensor([1, 1, 1, 1]),
        )
    ) == pytest.approx(
        [
            -0.91893853,
            -1.41893853,
            -1.41893853,
            -0.91893853,
        ],
    )

    # Allow poisson(lambda=0) under limit Poisson(n = 0 | lambda -> 0) = 1
    assert tb.tolist(
        tb.poisson(tb.astensor([0, 0, 1, 1]), tb.astensor([0, 1, 0, 1]))
    ) == pytest.approx([1.0, 0.3678794503211975, 0.0, 0.3678794503211975])
    assert tb.tolist(
        tb.poisson_logpdf(tb.astensor([0, 0, 1, 1]), tb.astensor([0, 1, 0, 1]))
    ) == pytest.approx(
        np.log([1.0, 0.3678794503211975, 0.0, 0.3678794503211975]).tolist()
    )

    # Ensure continuous approximation is valid
    assert tb.tolist(
        tb.poisson(n=tb.astensor([0.5, 1.1, 1.5]), lam=tb.astensor(1.0))
    ) == pytest.approx([0.4151074974205947, 0.3515379040027489, 0.2767383316137298])


def test_boolean_mask(backend):
    tb = pyhf.tensorlib
    assert tb.tolist(
        tb.boolean_mask(
            tb.astensor([1, 2, 3, 4, 5, 6]),
            tb.astensor([True, True, False, True, False, False], dtype='bool'),
        )
    ) == [1, 2, 4]
    assert tb.tolist(
        tb.boolean_mask(
            tb.astensor([[1, 2], [3, 4], [5, 6]]),
            tb.astensor([[True, True], [False, True], [False, False]], dtype='bool'),
        )
    ) == [1, 2, 4]


def test_percentile(backend):
    tb = pyhf.tensorlib
    a = tb.astensor([[10, 7, 4], [3, 2, 1]])
    assert tb.tolist(tb.percentile(a, 0)) == 1

    assert tb.tolist(tb.percentile(a, 50)) == 3.5
    assert tb.tolist(tb.percentile(a, 100)) == 10
    assert tb.tolist(tb.percentile(a, 50, axis=1)) == [7.0, 2.0]


# FIXME: PyTorch doesn't yet support interpolation schemes other than "linear"
# c.f. https://github.com/pytorch/pytorch/pull/59397
# c.f. https://github.com/scikit-hep/pyhf/issues/1693
@pytest.mark.fail_pytorch
@pytest.mark.fail_pytorch64
def test_percentile_interpolation(backend):
    tb = pyhf.tensorlib
    a = tb.astensor([[10, 7, 4], [3, 2, 1]])

    assert tb.tolist(tb.percentile(a, 50, interpolation="linear")) == 3.5
    assert tb.tolist(tb.percentile(a, 50, interpolation="nearest")) == 3.0
    assert tb.tolist(tb.percentile(a, 50, interpolation="lower")) == 3.0
    assert tb.tolist(tb.percentile(a, 50, interpolation="midpoint")) == 3.5
    assert tb.tolist(tb.percentile(a, 50, interpolation="higher")) == 4.0


def test_tensor_tile(backend):
    a = [[1], [2], [3]]
    tb = pyhf.tensorlib
    assert tb.tolist(tb.tile(tb.astensor(a), (1, 2))) == [[1, 1], [2, 2], [3, 3]]

    a = [1, 2, 3]
    assert tb.tolist(tb.tile(tb.astensor(a), (2,))) == [1, 2, 3, 1, 2, 3]

    a = [10, 20]
    assert tb.tolist(tb.tile(tb.astensor(a), (2, 1))) == [[10, 20], [10, 20]]
    assert tb.tolist(tb.tile(tb.astensor(a), (2, 1, 3))) == [
        [[10.0, 20.0, 10.0, 20.0, 10.0, 20.0]],
        [[10.0, 20.0, 10.0, 20.0, 10.0, 20.0]],
    ]

    if tb.name == 'tensorflow':
        with pytest.raises(tf.errors.InvalidArgumentError):
            tb.tile(tb.astensor([[[10, 20, 30]]]), (2, 1))


def test_1D_gather(backend):
    tb = pyhf.tensorlib
    assert tb.tolist(
        tb.gather(
            tb.astensor([1, 2, 3, 4, 5, 6]), tb.astensor([4, 0, 3, 2], dtype='int')
        )
    ) == [5, 1, 4, 3]
    assert tb.tolist(
        tb.gather(
            tb.astensor([1, 2, 3, 4, 5, 6]), tb.astensor([[4, 0], [3, 2]], dtype='int')
        )
    ) == [[5, 1], [4, 3]]


def test_ND_gather(backend):
    tb = pyhf.tensorlib
    assert tb.tolist(
        tb.gather(
            tb.astensor([[1, 2], [3, 4], [5, 6]]), tb.astensor([1, 0], dtype='int')
        )
    ) == [[3, 4], [1, 2]]


def test_isfinite(backend):
    tb = pyhf.tensorlib
    assert tb.tolist(tb.isfinite(tb.astensor([1.0, float("nan"), float("inf")]))) == [
        True,
        False,
        False,
    ]


def test_einsum(backend):
    tb = pyhf.tensorlib
    x = np.arange(20).reshape(5, 4).tolist()

    assert np.all(
        tb.tolist(tb.einsum('ij->ji', tb.astensor(x))) == np.asarray(x).T.tolist()
    )
    assert (
        tb.tolist(tb.einsum('i,j->ij', tb.astensor([1, 1, 1]), tb.astensor([1, 2, 3])))
        == [[1, 2, 3]] * 3
    )


def test_list_to_list(backend):
    tb = pyhf.tensorlib
    # test when no other tensor operations are done
    assert tb.tolist([1, 2, 3, 4]) == [1, 2, 3, 4]
    assert tb.tolist([[1], [2], [3], [4]]) == [[1], [2], [3], [4]]
    assert tb.tolist([[1, 2], 3, [4]]) == [[1, 2], 3, [4]]


def test_tensor_to_list(backend):
    tb = pyhf.tensorlib
    assert tb.tolist(tb.astensor([1, 2, 3, 4])) == [1, 2, 3, 4]
    assert tb.tolist(tb.astensor([[1], [2], [3], [4]])) == [[1], [2], [3], [4]]


@pytest.mark.only_tensorflow
def test_tensor_list_conversion(backend):
    tb = pyhf.tensorlib
    # test when a tensor operation is done, but then need to check if this
    # doesn't break in session.run
    assert tb.tolist(tb.astensor([1, 2, 3, 4])) == [1, 2, 3, 4]
    assert tb.tolist([1, 2, 3, 4]) == [1, 2, 3, 4]


def test_pdf_eval(backend):
    source = {
        "binning": [2, -0.5, 1.5],
        "bindata": {
            "data": [120.0, 180.0],
            "bkg": [100.0, 150.0],
            "bkgsys_up": [102, 190],
            "bkgsys_dn": [98, 100],
            "sig": [30.0, 95.0],
        },
    }
    spec = {
        'channels': [
            {
                'name': 'singlechannel',
                'samples': [
                    {
                        'name': 'signal',
                        'data': source['bindata']['sig'],
                        'modifiers': [
                            {'name': 'mu', 'type': 'normfactor', 'data': None}
                        ],
                    },
                    {
                        'name': 'background',
                        'data': source['bindata']['bkg'],
                        'modifiers': [
                            {
                                'name': 'bkg_norm',
                                'type': 'histosys',
                                'data': {
                                    'lo_data': source['bindata']['bkgsys_dn'],
                                    'hi_data': source['bindata']['bkgsys_up'],
                                },
                            }
                        ],
                    },
                ],
            }
        ]
    }
    pdf = pyhf.Model(spec)
    data = source['bindata']['data'] + pdf.config.auxdata
    assert pytest.approx([-17.648827643136507], rel=5e-5) == pyhf.tensorlib.tolist(
        pdf.logpdf(pdf.config.suggested_init(), data)
    )


def test_pdf_eval_2(backend):
    source = {
        "binning": [2, -0.5, 1.5],
        "bindata": {
            "data": [120.0, 180.0],
            "bkg": [100.0, 150.0],
            "bkgerr": [10.0, 10.0],
            "sig": [30.0, 95.0],
        },
    }

    pdf = uncorrelated_background(
        source['bindata']['sig'], source['bindata']['bkg'], source['bindata']['bkgerr']
    )
    data = source['bindata']['data'] + pdf.config.auxdata

    assert pytest.approx([-23.579605171119738], rel=5e-5) == pyhf.tensorlib.tolist(
        pdf.logpdf(pdf.config.suggested_init(), data)
    )


def test_tensor_precision(backend):
    tb, _ = backend
    assert tb.precision in ['32b', '64b']


@pytest.mark.parametrize(
    'tensorlib',
    ['numpy_backend', 'jax_backend', 'pytorch_backend', 'tensorflow_backend'],
)
@pytest.mark.parametrize('precision', ['64b', '32b'])
def test_set_tensor_precision(tensorlib, precision):
    tb = getattr(pyhf.tensor, tensorlib)(precision=precision)
    assert tb.precision == precision
    # check for float64/int64/float32/int32 in the dtypemap by looking at the class names
    #   - may break if class names stop including this, but i doubt it
    assert f'float{precision[:1]}' in str(tb.dtypemap['float'])
    assert f'int{precision[:1]}' in str(tb.dtypemap['int'])


def test_trigger_tensorlib_changed_name(mocker):
    numpy_64 = pyhf.tensor.numpy_backend(precision='64b')
    jax_64 = pyhf.tensor.jax_backend(precision='64b')

    pyhf.set_backend(numpy_64)

    func = mocker.Mock()
    pyhf.events.subscribe('tensorlib_changed')(func.__call__)

    assert func.call_count == 0
    pyhf.set_backend(jax_64)
    assert func.call_count == 1


def test_trigger_tensorlib_changed_precision(mocker):
    jax_64 = pyhf.tensor.jax_backend(precision='64b')
    jax_32 = pyhf.tensor.jax_backend(precision='32b')

    pyhf.set_backend(jax_64)

    func = mocker.Mock()
    pyhf.events.subscribe('tensorlib_changed')(func.__call__)

    assert func.call_count == 0
    pyhf.set_backend(jax_32)
    assert func.call_count == 1


@pytest.mark.parametrize(
    'tensorlib',
    ['numpy_backend', 'jax_backend', 'pytorch_backend', 'tensorflow_backend'],
)
@pytest.mark.parametrize('precision', ['64b', '32b'])
def test_tensorlib_setup(tensorlib, precision, mocker):
    tb = getattr(pyhf.tensor, tensorlib)(precision=precision)

    func = mocker.patch(f'pyhf.tensor.{tensorlib}._setup')
    assert func.call_count == 0
    pyhf.set_backend(tb)
    assert func.call_count == 1
