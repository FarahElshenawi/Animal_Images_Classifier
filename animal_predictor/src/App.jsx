import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setImage(file);
    setError('');
    setResult(null);

    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    } else {
      setImagePreview(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!image) {
      setError('Please upload an image');
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    formData.append('image', image);

    try {
      const response = await axios.post('http://localhost:5000/predict', formData);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Prediction failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Add this function near your other handlers
  const handleReset = () => {
    setImage(null);
    setImagePreview(null);
    setResult(null);
    setError('');
  };

  return (
    <div className="container py-5">
      <div className="text-center mb-5">
        <i className="fas fa-paw fa-4x text-primary mb-3"></i>
        <h1 className="display-4">Animal Image Classifier</h1>
        <p className="lead text-muted">Upload an image and let AI identify the animal species.</p>
      </div>

      <div className={`content-layout ${result ? 'split' : 'centered'}`}>
        {/* Upload Section */}
        <div className="upload-section">
          <div className="card shadow-sm p-4">
            <form onSubmit={handleSubmit}>
              <div className="upload-area mb-4">
                <input
                  type="file"
                  className="form-control d-none"
                  id="imageUpload"
                  accept="image/*"
                  onChange={handleFileChange}
                  required
                />
                <label htmlFor="imageUpload" className="mb-0 w-100">
                  {imagePreview ? (
                    <div style={{ position: 'relative' }}>
                      <img
                        src={imagePreview}
                        alt="Preview"
                        className="img-preview rounded"
                        style={{ maxHeight: '300px', maxWidth: '100%', objectFit: 'contain' }}
                      />
                      {isLoading && (
                        <div className="image-overlay">
                          <div className="spinner"></div>
                          <p className="mt-3 mb-0">Processing...</p>
                        </div>
                      )}
                    </div>
                  ) : (
                    <>
                      <i className="fas fa-cloud-upload-alt fa-3x text-primary mb-3"></i>
                      <p>Click or drag image here</p>
                    </>
                  )}
                </label>
              </div>
              <div className="d-flex gap-2">
                <button
                  type="submit"
                  className={`btn btn-primary fw-bold ${imagePreview ? 'flex-grow-1' : 'w-100'}`}
                  disabled={isLoading}
                >
                  <i className="fas fa-brain me-2"></i>Predict Animal
                </button>
                {imagePreview && (
                  <button
                    type="button"
                    className="btn btn-secondary fw-bold"
                    onClick={handleReset}
                    disabled={isLoading}
                  >
                    <i className="fas fa-redo me-2"></i>Reset
                  </button>
                )}
              </div>
            </form>
            {error && (
              <div className="alert alert-danger mt-3">
                <i className="fas fa-exclamation-triangle me-2"></i>{error}
              </div>
            )}
          </div>
        </div>

        {/* Results Section */}
        {result && (
          <div className="results-section">
            <div className="card shadow-sm p-4 result-appear">
              <div className="text-center mb-3">
                <i className="fas fa-check-circle fa-2x text-success"></i>
                <h5 className="mt-3">Prediction Result</h5>
              </div>
              <p className="text-center"><strong>Animal:</strong> {result.prediction}</p>
              <p className="text-center"><strong>Confidence:</strong> {result.confidence}</p>

              <h6 className="mt-4 mb-3">All Predictions</h6>
              <div className="table-responsive">
                <table className="table table-hover table-bordered">
                  <thead className="table-light">
                    <tr>
                      <th>Class</th>
                      <th>Confidence (%)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.all_predictions.map((pred, index) => (
                      <tr key={index}>
                        <td>{pred.class}</td>
                        <td>{pred.confidence.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
