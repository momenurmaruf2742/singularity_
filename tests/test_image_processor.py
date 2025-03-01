import os
import sys

import pytest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.image_processor import HighDimImageProcessor
import numpy as np

def test_get_slice():
    # Create a dummy 5D image
    image = np.random.rand(10, 10, 5, 3, 4)  # X, Y, Z, Time, Channel
    processor = HighDimImageProcessor("dummy_path")
    processor.image = image

    # Test slicing with valid parameters
    slice_data = processor.get_slice(z=2, time=1, channel=3)
    assert slice_data.shape == (10, 10)

    # Test slicing with invalid parameters (should raise IndexError)
    with pytest.raises(IndexError):
        processor.get_slice(z=10, time=1, channel=3)  # z out of bounds

    # Test slicing without parameters (should return the entire image)
    full_image = processor.get_slice()
    assert full_image.shape == image.shape

    # Test slicing on a 2D image
    image_2d = np.random.rand(10, 10)  # X, Y
    processor.image = image_2d
    slice_2d = processor.get_slice()
    assert slice_2d.shape == (10, 10)

def test_calculate_statistics():
    # Create a dummy 5D image
    image = np.random.rand(10, 10, 5, 3, 4)  # X, Y, Z, Time, Channel
    processor = HighDimImageProcessor("dummy_path")
    processor.image = image

    # Test statistics for 5D image
    stats = processor.calculate_statistics()
    assert "mean" in stats
    assert "std" in stats
    assert "min" in stats
    assert "max" in stats

    # Validate the computed statistics
    assert np.allclose(stats["mean"], np.mean(image, axis=(0, 1, 2, 3)))
    assert np.allclose(stats["std"], np.std(image, axis=(0, 1, 2, 3)))
    assert np.allclose(stats["min"], np.min(image, axis=(0, 1, 2, 3)))
    assert np.allclose(stats["max"], np.max(image, axis=(0, 1, 2, 3)))

    # Test statistics for 2D image
    image_2d = np.random.rand(10, 10)  # X, Y
    processor.image = image_2d
    stats_2d = processor.calculate_statistics()
    assert "mean" in stats_2d
    assert "std" in stats_2d
    assert "min" in stats_2d
    assert "max" in stats_2d

    # Test statistics for empty image (should raise ValueError)
    processor.image = np.array([])
    with pytest.raises(ValueError):
        processor.calculate_statistics()