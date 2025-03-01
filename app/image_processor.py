import numpy as np
from skimage import io, filters
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

class HighDimImageProcessor:
    def __init__(self, image_path):
        self.image = io.imread(image_path)
        self.dimensions = self.image.shape
        print(f"Loaded image with dimensions: {self.dimensions}")  # Debug statement

    def get_slice(self, z=None, time=None, channel=None):
        """Extract a specific slice from the 5D image."""
        slice_idx = [slice(None)] * len(self.dimensions)
        if z is not None:
            slice_idx[2] = z
        if time is not None:
            slice_idx[3] = time
        if channel is not None:
            slice_idx[4] = channel
        return self.image[tuple(slice_idx)]

    def perform_pca(self, n_components=3):
        """Perform PCA for dimensionality reduction."""
        flattened = self.image.reshape(-1, self.dimensions[-1])
        pca = PCA(n_components=n_components)
        reduced = pca.fit_transform(flattened)
        return reduced.reshape(self.dimensions[:-1] + (n_components,))

    def calculate_statistics(self):
        """Calculate image statistics (mean, std, min, max) for each band."""
        if len(self.dimensions) == 2:  # 2D image (X, Y)
            stats = {
                "mean": float(np.mean(self.image)),
                "std": float(np.std(self.image)),
                "min": float(np.min(self.image)),
                "max": float(np.max(self.image)),
            }
        elif len(self.dimensions) == 3:  # 3D image (X, Y, Z or X, Y, Channel)
            stats = {
                "mean": np.mean(self.image, axis=(0, 1)).tolist(),
                "std": np.std(self.image, axis=(0, 1)).tolist(),
                "min": np.min(self.image, axis=(0, 1)).tolist(),
                "max": np.max(self.image, axis=(0, 1)).tolist(),
            }
        elif len(self.dimensions) == 4:  # 4D image (X, Y, Z, Time or X, Y, Time, Channel)
            stats = {
                "mean": np.mean(self.image, axis=(0, 1, 2)).tolist(),
                "std": np.std(self.image, axis=(0, 1, 2)).tolist(),
                "min": np.min(self.image, axis=(0, 1, 2)).tolist(),
                "max": np.max(self.image, axis=(0, 1, 2)).tolist(),
            }
        elif len(self.dimensions) == 5:  # 5D image (X, Y, Z, Time, Channel)
            stats = {
                "mean": np.mean(self.image, axis=(0, 1, 2, 3)).tolist(),
                "std": np.std(self.image, axis=(0, 1, 2, 3)).tolist(),
                "min": np.min(self.image, axis=(0, 1, 2, 3)).tolist(),
                "max": np.max(self.image, axis=(0, 1, 2, 3)).tolist(),
            }
        else:
            raise ValueError("Unsupported image dimensions.")
        return stats

    def segment_image(self, channel, method="kmeans"):
        """Apply segmentation on a specific channel."""
        channel_data = self.get_slice(channel=channel)
        if method == "kmeans":
            kmeans = KMeans(n_clusters=2)
            labels = kmeans.fit_predict(channel_data.reshape(-1, 1))
            return labels.reshape(channel_data.shape)
        elif method == "otsu":
            return channel_data > filters.threshold_otsu(channel_data)