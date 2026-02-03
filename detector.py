"""
Advanced AI Voice Detection Engine
Multi-technique ensemble approach for high accuracy detection
"""

import io
import numpy as np
import logging
from typing import Tuple, Literal, Dict, List
import warnings
import hashlib

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

# Import audio processing libraries
try:
    import librosa
    import librosa.display
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning("librosa not available")

try:
    from scipy import stats, signal
    from scipy.fft import fft, fftfreq
    from scipy.ndimage import uniform_filter1d
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("scipy not available")

# Try to import deep learning libraries
try:
    import torch
    import torchaudio
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("torch/torchaudio not available")


class AdvancedVoiceAnalyzer:
    """
    Advanced voice analysis using multiple detection techniques
    """
    
    def __init__(self):
        self.sample_rate = 16000
        self.n_fft = 2048
        self.hop_length = 512
        self.n_mels = 128
        self.n_mfcc = 40
        
    def load_audio(self, audio_data: bytes) -> Tuple[np.ndarray, int]:
        """Load audio from bytes with multiple fallback methods"""
        import tempfile
        import os
        
        logger.info(f"Attempting to load audio: {len(audio_data)} bytes")
        logger.info(f"First 20 bytes (hex): {audio_data[:20].hex()}")
        
        # Method 1: Try librosa with BytesIO
        if LIBROSA_AVAILABLE:
            try:
                audio_buffer = io.BytesIO(audio_data)
                y, sr = librosa.load(audio_buffer, sr=self.sample_rate, mono=True)
                if len(y) > 0:
                    logger.info(f"Librosa BytesIO succeeded: {len(y)} samples")
                    return y, sr
            except Exception as e:
                logger.warning(f"Librosa BytesIO failed: {e}")
        
        # Method 2: Try librosa with temp file
        if LIBROSA_AVAILABLE:
            try:
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                    tmp.write(audio_data)
                    tmp_path = tmp.name
                
                y, sr = librosa.load(tmp_path, sr=self.sample_rate, mono=True)
                os.unlink(tmp_path)
                if len(y) > 0:
                    logger.info(f"Librosa temp file succeeded: {len(y)} samples")
                    return y, sr
            except Exception as e:
                logger.warning(f"Librosa temp file failed: {e}")
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        
        # Method 3: Try torchaudio
        if TORCH_AVAILABLE:
            try:
                audio_buffer = io.BytesIO(audio_data)
                waveform, sr = torchaudio.load(audio_buffer)
                # Resample if needed
                if sr != self.sample_rate:
                    resampler = torchaudio.transforms.Resample(sr, self.sample_rate)
                    waveform = resampler(waveform)
                # Convert to mono
                if waveform.shape[0] > 1:
                    waveform = torch.mean(waveform, dim=0, keepdim=True)
                logger.info(f"Torchaudio succeeded: {waveform.squeeze().shape[0]} samples")
                return waveform.squeeze().numpy(), self.sample_rate
            except Exception as e:
                logger.warning(f"Torchaudio failed: {e}")
        
        # Method 4: Try soundfile directly
        try:
            import soundfile as sf
            audio_buffer = io.BytesIO(audio_data)
            y, sr = sf.read(audio_buffer)
            if len(y.shape) > 1:
                y = np.mean(y, axis=1)  # Convert to mono
            # Resample if needed
            if sr != self.sample_rate:
                y = librosa.resample(y, orig_sr=sr, target_sr=self.sample_rate)
                sr = self.sample_rate
            logger.info(f"Soundfile succeeded: {len(y)} samples")
            return y, sr
        except Exception as e:
            logger.warning(f"Soundfile failed: {e}")
        
        raise ValueError("Could not load audio with any available method")

    def analyze_spectral_artifacts(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Detect AI-specific spectral artifacts
        AI synthesizers often leave characteristic patterns in the spectrum
        """
        features = {}
        
        try:
            # Compute spectrogram
            D = np.abs(librosa.stft(y, n_fft=self.n_fft, hop_length=self.hop_length))
            D_db = librosa.amplitude_to_db(D, ref=np.max)
            
            # 1. Spectral smoothness - AI tends to be TOO smooth
            spectral_diff = np.diff(D_db, axis=0)
            features['spectral_smoothness'] = np.mean(np.abs(spectral_diff))
            
            # 2. Frequency band energy distribution
            # Split into bands and compare
            n_bands = 8
            band_size = D.shape[0] // n_bands
            band_energies = []
            for i in range(n_bands):
                start = i * band_size
                end = (i + 1) * band_size
                band_energy = np.mean(D[start:end, :])
                band_energies.append(band_energy)
            
            band_energies = np.array(band_energies)
            features['band_energy_std'] = np.std(band_energies)
            features['band_energy_range'] = np.max(band_energies) - np.min(band_energies)
            
            # 3. High frequency content (AI often lacks natural high-freq detail)
            high_freq_start = int(D.shape[0] * 0.7)
            high_freq_energy = np.mean(D[high_freq_start:, :])
            low_freq_energy = np.mean(D[:high_freq_start, :])
            features['high_low_freq_ratio'] = high_freq_energy / (low_freq_energy + 1e-10)
            
            # 4. Spectral flux (rate of change)
            spectral_flux = np.sqrt(np.sum(np.diff(D, axis=1) ** 2, axis=0))
            features['spectral_flux_mean'] = np.mean(spectral_flux)
            features['spectral_flux_std'] = np.std(spectral_flux)
            features['spectral_flux_max'] = np.max(spectral_flux)
            
            # 5. Sub-band spectral flux (different frequency regions)
            for i, (start, end) in enumerate([(0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.0)]):
                start_idx = int(D.shape[0] * start)
                end_idx = int(D.shape[0] * end)
                subband_flux = np.sqrt(np.sum(np.diff(D[start_idx:end_idx, :], axis=1) ** 2, axis=0))
                features[f'subband_flux_{i}_mean'] = np.mean(subband_flux)
                features[f'subband_flux_{i}_std'] = np.std(subband_flux)
            
            # 6. Spectral centroid variation
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length)[0]
            features['spectral_centroid_mean'] = np.mean(spectral_centroid)
            features['spectral_centroid_std'] = np.std(spectral_centroid)
            features['spectral_centroid_range'] = np.max(spectral_centroid) - np.min(spectral_centroid)
            
            # 7. Spectral bandwidth
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length)[0]
            features['spectral_bandwidth_mean'] = np.mean(spectral_bandwidth)
            features['spectral_bandwidth_std'] = np.std(spectral_bandwidth)
            
            # 8. Spectral rolloff (frequency below which 85% of energy is contained)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length)[0]
            features['spectral_rolloff_mean'] = np.mean(spectral_rolloff)
            features['spectral_rolloff_std'] = np.std(spectral_rolloff)
            
            # 9. Spectral flatness (how noise-like vs tonal)
            spectral_flatness = librosa.feature.spectral_flatness(y=y, n_fft=self.n_fft, hop_length=self.hop_length)[0]
            features['spectral_flatness_mean'] = np.mean(spectral_flatness)
            features['spectral_flatness_std'] = np.std(spectral_flatness)
            features['spectral_flatness_max'] = np.max(spectral_flatness)
            
            # 10. Spectral contrast
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length)
            features['spectral_contrast_mean'] = np.mean(spectral_contrast)
            features['spectral_contrast_std'] = np.std(spectral_contrast)
            
        except Exception as e:
            logger.warning(f"Spectral artifact analysis failed: {e}")
        
        return features

    def analyze_temporal_patterns(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Analyze temporal patterns that differ between AI and human speech
        """
        features = {}
        
        try:
            # 1. RMS energy over time
            rms = librosa.feature.rms(y=y, frame_length=self.n_fft, hop_length=self.hop_length)[0]
            features['rms_mean'] = np.mean(rms)
            features['rms_std'] = np.std(rms)
            features['rms_max'] = np.max(rms)
            features['rms_min'] = np.min(rms)
            features['rms_range'] = features['rms_max'] - features['rms_min']
            
            # Dynamic range (humans have more dynamic variation)
            features['dynamic_range'] = 20 * np.log10((features['rms_max'] + 1e-10) / (features['rms_min'] + 1e-10))
            
            # 2. Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y, frame_length=self.n_fft, hop_length=self.hop_length)[0]
            features['zcr_mean'] = np.mean(zcr)
            features['zcr_std'] = np.std(zcr)
            features['zcr_max'] = np.max(zcr)
            
            # 3. Autocorrelation analysis (periodicity)
            autocorr = np.correlate(y, y, mode='same')
            autocorr = autocorr[len(autocorr)//2:]  # Take positive lags only
            autocorr = autocorr / autocorr[0]  # Normalize
            
            # Find peaks in autocorrelation (indicates periodicity)
            if SCIPY_AVAILABLE:
                peaks, _ = signal.find_peaks(autocorr, height=0.3, distance=100)
                features['autocorr_num_peaks'] = len(peaks)
                if len(peaks) > 1:
                    features['autocorr_peak_regularity'] = np.std(np.diff(peaks))
                else:
                    features['autocorr_peak_regularity'] = 0
            
            # 4. Energy envelope analysis
            # Compute envelope using Hilbert transform
            if SCIPY_AVAILABLE:
                analytic_signal = signal.hilbert(y)
                amplitude_envelope = np.abs(analytic_signal)
                
                # Envelope statistics
                features['envelope_mean'] = np.mean(amplitude_envelope)
                features['envelope_std'] = np.std(amplitude_envelope)
                
                # Envelope smoothness (AI tends to be smoother)
                envelope_diff = np.diff(amplitude_envelope)
                features['envelope_roughness'] = np.mean(np.abs(envelope_diff))
                
                # Envelope modulation rate
                envelope_fft = np.abs(fft(amplitude_envelope - np.mean(amplitude_envelope)))[:len(amplitude_envelope)//2]
                features['envelope_modulation_energy'] = np.sum(envelope_fft[:100])  # Low frequency modulation
            
            # 5. Silence/pause detection
            # Count frames below threshold
            silence_threshold = 0.01 * np.max(rms)
            silent_frames = np.sum(rms < silence_threshold)
            features['silence_ratio'] = silent_frames / len(rms)
            
            # 5.5 ZCR range (humans have more variation)
            features['zcr_range'] = np.max(zcr) - np.min(zcr)
            
            # 5.6 RMS range
            features['rms_range'] = np.max(rms) - np.min(rms)
            
            # 5.7 Envelope irregularity (frame-to-frame variation)
            if 'amplitude_envelope' in dir():
                frame_size = 256
                n_env_frames = len(amplitude_envelope) // frame_size
                if n_env_frames > 2:
                    env_frames = amplitude_envelope[:n_env_frames * frame_size].reshape(n_env_frames, frame_size)
                    env_frame_energy = np.mean(env_frames, axis=1)
                    features['envelope_irregularity'] = np.std(np.diff(env_frame_energy))
            
            # 5.8 Autocorrelation peak ratio (consistency of periodicity)
            if 'autocorr' in dir() and len(autocorr) > 200:
                main_peak = np.max(autocorr[50:200]) if len(autocorr) > 200 else 0
                features['autocorr_peak_ratio'] = main_peak
            
            # 6. Energy attack/decay patterns
            # Find energy onsets
            onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)
            features['onset_strength_mean'] = np.mean(onset_env)
            features['onset_strength_std'] = np.std(onset_env)
            
            onsets = librosa.onset.onset_detect(y=y, sr=sr, hop_length=self.hop_length, units='time')
            features['num_onsets'] = len(onsets)
            if len(onsets) > 1:
                onset_intervals = np.diff(onsets)
                features['onset_interval_mean'] = np.mean(onset_intervals)
                features['onset_interval_std'] = np.std(onset_intervals)
            
        except Exception as e:
            logger.warning(f"Temporal pattern analysis failed: {e}")
        
        return features

    def analyze_mfcc_patterns(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Deep MFCC analysis - key discriminator for AI voices
        """
        features = {}
        
        try:
            # Compute MFCCs
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc, n_fft=self.n_fft, hop_length=self.hop_length)
            
            # 1. Basic MFCC statistics
            for i in range(min(20, self.n_mfcc)):  # First 20 coefficients
                features[f'mfcc_{i}_mean'] = np.mean(mfcc[i])
                features[f'mfcc_{i}_std'] = np.std(mfcc[i])
            
            # 2. Overall MFCC statistics
            features['mfcc_overall_mean'] = np.mean(mfcc)
            features['mfcc_overall_std'] = np.std(mfcc)
            features['mfcc_overall_var'] = np.var(mfcc)
            
            # 3. MFCC deltas (first derivative - temporal dynamics)
            mfcc_delta = librosa.feature.delta(mfcc)
            features['mfcc_delta_mean'] = np.mean(np.abs(mfcc_delta))
            features['mfcc_delta_std'] = np.std(mfcc_delta)
            features['mfcc_delta_max'] = np.max(np.abs(mfcc_delta))
            
            # 4. MFCC delta-deltas (second derivative - acceleration)
            mfcc_delta2 = librosa.feature.delta(mfcc, order=2)
            features['mfcc_delta2_mean'] = np.mean(np.abs(mfcc_delta2))
            features['mfcc_delta2_std'] = np.std(mfcc_delta2)
            
            # 5. MFCC correlation matrix analysis
            # AI voices often have different inter-coefficient correlations
            mfcc_corr = np.corrcoef(mfcc)
            features['mfcc_corr_mean'] = np.mean(mfcc_corr)
            features['mfcc_corr_std'] = np.std(mfcc_corr)
            
            # Off-diagonal correlations
            off_diag = mfcc_corr[np.triu_indices(len(mfcc_corr), k=1)]
            features['mfcc_corr_offdiag_mean'] = np.mean(off_diag)
            features['mfcc_corr_offdiag_std'] = np.std(off_diag)
            
            # 6. Temporal consistency of MFCCs
            # How much do MFCCs change frame to frame
            mfcc_frame_diff = np.diff(mfcc, axis=1)
            features['mfcc_temporal_diff_mean'] = np.mean(np.abs(mfcc_frame_diff))
            features['mfcc_temporal_diff_std'] = np.std(mfcc_frame_diff)
            
            # 7. MFCC skewness and kurtosis
            if SCIPY_AVAILABLE:
                features['mfcc_skewness'] = np.mean([stats.skew(mfcc[i]) for i in range(mfcc.shape[0])])
                features['mfcc_kurtosis'] = np.mean([stats.kurtosis(mfcc[i]) for i in range(mfcc.shape[0])])
            
        except Exception as e:
            logger.warning(f"MFCC analysis failed: {e}")
        
        return features

    def analyze_pitch_and_prosody(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Analyze pitch and prosody patterns
        AI voices often have unnatural pitch patterns
        """
        features = {}
        
        try:
            # 1. Pitch tracking using piptrack
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length)
            
            # Extract pitch values (take max magnitude pitch per frame)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 50 and pitch < 500:  # Reasonable voice pitch range
                    pitch_values.append(pitch)
            
            if len(pitch_values) > 10:
                pitch_values = np.array(pitch_values)
                
                features['pitch_mean'] = np.mean(pitch_values)
                features['pitch_std'] = np.std(pitch_values)
                features['pitch_median'] = np.median(pitch_values)
                features['pitch_range'] = np.max(pitch_values) - np.min(pitch_values)
                features['pitch_iqr'] = np.percentile(pitch_values, 75) - np.percentile(pitch_values, 25)
                
                # Pitch coefficient of variation (normalized variability)
                features['pitch_cv'] = features['pitch_std'] / (features['pitch_mean'] + 1e-10)
                
                # Pitch contour smoothness
                pitch_diff = np.diff(pitch_values)
                features['pitch_diff_mean'] = np.mean(np.abs(pitch_diff))
                features['pitch_diff_std'] = np.std(pitch_diff)
                features['pitch_diff_max'] = np.max(np.abs(pitch_diff))
                
                # Pitch jitter (rapid pitch variations) - important for naturalness
                jitter = np.mean(np.abs(np.diff(pitch_values))) / (features['pitch_mean'] + 1e-10)
                features['pitch_jitter'] = jitter
                
                # Pitch skewness and kurtosis
                if SCIPY_AVAILABLE:
                    features['pitch_skewness'] = stats.skew(pitch_values)
                    features['pitch_kurtosis'] = stats.kurtosis(pitch_values)
            
            # 2. Harmonic analysis
            harmonic, percussive = librosa.effects.hpss(y)
            
            features['harmonic_mean'] = np.mean(np.abs(harmonic))
            features['harmonic_std'] = np.std(harmonic)
            features['percussive_mean'] = np.mean(np.abs(percussive))
            features['percussive_std'] = np.std(percussive)
            features['harmonic_percussive_ratio'] = features['harmonic_mean'] / (features['percussive_mean'] + 1e-10)
            
            # 3. Formant-like analysis using LPC
            # Get spectral peaks that might correspond to formants
            S = np.abs(librosa.stft(y, n_fft=self.n_fft, hop_length=self.hop_length))
            S_mean = np.mean(S, axis=1)
            
            if SCIPY_AVAILABLE:
                peaks, properties = signal.find_peaks(S_mean, height=np.max(S_mean) * 0.1, distance=10)
                features['num_spectral_peaks'] = len(peaks)
                if len(peaks) > 1:
                    features['spectral_peak_spacing_mean'] = np.mean(np.diff(peaks))
                    features['spectral_peak_spacing_std'] = np.std(np.diff(peaks))
            
        except Exception as e:
            logger.warning(f"Pitch analysis failed: {e}")
        
        return features

    def analyze_phase_patterns(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Analyze phase information - AI vocoders often have phase artifacts
        """
        features = {}
        
        try:
            # Compute STFT with phase
            D = librosa.stft(y, n_fft=self.n_fft, hop_length=self.hop_length)
            magnitude = np.abs(D)
            phase = np.angle(D)
            
            # 1. Phase derivative (instantaneous frequency deviation)
            phase_diff = np.diff(phase, axis=1)
            # Unwrap phase differences
            phase_diff = np.mod(phase_diff + np.pi, 2 * np.pi) - np.pi
            
            features['phase_diff_mean'] = np.mean(np.abs(phase_diff))
            features['phase_diff_std'] = np.std(phase_diff)
            
            # 2. Group delay deviation
            # In natural speech, group delay varies; AI might be more regular
            group_delay = -np.diff(phase, axis=0) / (2 * np.pi * self.hop_length / sr)
            features['group_delay_std'] = np.std(group_delay)
            
            # 3. Phase coherence across frequency bands
            # AI vocoders might have unusual phase relationships
            n_bands = 4
            band_size = phase.shape[0] // n_bands
            band_coherences = []
            for i in range(n_bands - 1):
                band1 = phase[i * band_size:(i + 1) * band_size, :]
                band2 = phase[(i + 1) * band_size:(i + 2) * band_size, :]
                # Compute phase coherence
                coherence = np.mean(np.cos(band1[:min(band1.shape[0], band2.shape[0])] - 
                                          band2[:min(band1.shape[0], band2.shape[0])]))
                band_coherences.append(coherence)
            
            features['phase_band_coherence_mean'] = np.mean(band_coherences)
            features['phase_band_coherence_std'] = np.std(band_coherences)
            
            # 3.5 Overall phase coherence (AI tends to be more coherent)
            features['phase_coherence'] = np.mean(np.abs(np.cos(phase_diff)))
            
            # 4. Magnitude-phase relationship
            # Natural speech has specific magnitude-phase relationships
            mag_phase_corr = np.corrcoef(magnitude.flatten()[:10000], 
                                         np.abs(phase).flatten()[:10000])[0, 1]
            features['mag_phase_correlation'] = mag_phase_corr if not np.isnan(mag_phase_corr) else 0
            
        except Exception as e:
            logger.warning(f"Phase analysis failed: {e}")
        
        return features

    def analyze_noise_patterns(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Analyze noise characteristics
        AI voices often have different noise profiles
        """
        features = {}
        
        try:
            # 1. Estimate noise floor
            S = np.abs(librosa.stft(y, n_fft=self.n_fft, hop_length=self.hop_length))
            
            # Use minimum statistics for noise floor estimation
            S_min = np.percentile(S, 5, axis=1)
            S_mean = np.mean(S, axis=1)
            
            features['noise_floor_mean'] = np.mean(S_min)
            features['noise_floor_std'] = np.std(S_min)
            features['snr_estimate'] = np.mean(S_mean) / (np.mean(S_min) + 1e-10)
            
            # 2. Spectral noise-like regions
            flatness = librosa.feature.spectral_flatness(y=y, n_fft=self.n_fft, hop_length=self.hop_length)[0]
            
            # High flatness indicates noise-like content
            noise_frames = np.sum(flatness > 0.5) / len(flatness)
            features['noise_frame_ratio'] = noise_frames
            
            # 3. Residual analysis after harmonic removal
            harmonic = librosa.effects.harmonic(y)
            residual = y - harmonic
            
            features['residual_energy'] = np.mean(residual ** 2)
            features['residual_ratio'] = features['residual_energy'] / (np.mean(y ** 2) + 1e-10)
            features['residual_variance'] = np.var(residual)
            
            # 4. High frequency noise analysis
            # AI often has cleaner or different HF noise
            nyquist = sr // 2
            hf_cutoff = int(0.7 * nyquist)
            
            if SCIPY_AVAILABLE:
                # High-pass filter
                sos = signal.butter(5, hf_cutoff, btype='high', fs=sr, output='sos')
                y_hf = signal.sosfilt(sos, y)
                features['hf_noise_energy'] = np.mean(y_hf ** 2)
                features['hf_noise_ratio'] = features['hf_noise_energy'] / (np.mean(y ** 2) + 1e-10)
            
        except Exception as e:
            logger.warning(f"Noise analysis failed: {e}")
        
        return features

    def analyze_statistical_moments(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Compute statistical moments of the waveform
        """
        features = {}
        
        try:
            # 1. Basic moments
            features['signal_mean'] = np.mean(y)
            features['signal_std'] = np.std(y)
            features['signal_var'] = np.var(y)
            
            if SCIPY_AVAILABLE:
                features['signal_skewness'] = stats.skew(y)
                features['signal_kurtosis'] = stats.kurtosis(y)
            
            # 2. Peak statistics
            features['signal_max'] = np.max(np.abs(y))
            features['signal_peak_count'] = len(signal.find_peaks(y, height=0.5 * np.max(y))[0]) if SCIPY_AVAILABLE else 0
            
            # Crest factor (peak to RMS ratio)
            rms = np.sqrt(np.mean(y ** 2))
            features['crest_factor'] = features['signal_max'] / (rms + 1e-10)
            
            # 3. Distribution analysis
            # Histogram-based features
            hist, bin_edges = np.histogram(y, bins=100, density=True)
            features['hist_entropy'] = -np.sum(hist[hist > 0] * np.log2(hist[hist > 0] + 1e-10))
            features['hist_peak'] = np.max(hist)
            features['hist_peak_position'] = bin_edges[np.argmax(hist)]
            
            # 4. Percentiles
            features['signal_p10'] = np.percentile(np.abs(y), 10)
            features['signal_p90'] = np.percentile(np.abs(y), 90)
            features['signal_p99'] = np.percentile(np.abs(y), 99)
            features['signal_iqr'] = np.percentile(np.abs(y), 75) - np.percentile(np.abs(y), 25)
            
        except Exception as e:
            logger.warning(f"Statistical analysis failed: {e}")
        
        return features

    def analyze_micro_modulations(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Analyze micro-modulations that distinguish human from AI voices
        Human voices have natural micro-variations that AI often lacks
        """
        features = {}
        
        try:
            # 1. Shimmer analysis (amplitude perturbation)
            # Extract short-term amplitude variations
            frame_length = int(0.025 * sr)  # 25ms frames
            hop_length = int(0.010 * sr)    # 10ms hop
            
            n_frames = (len(y) - frame_length) // hop_length + 1
            amplitudes = []
            for i in range(n_frames):
                start = i * hop_length
                end = start + frame_length
                frame = y[start:end]
                amplitudes.append(np.max(np.abs(frame)))
            
            if len(amplitudes) > 10:
                amplitudes = np.array(amplitudes)
                # Shimmer: average difference between consecutive amplitudes
                amp_diff = np.abs(np.diff(amplitudes))
                features['shimmer'] = np.mean(amp_diff) / (np.mean(amplitudes) + 1e-10)
                features['shimmer_db'] = 20 * np.log10(1 + features['shimmer'])
                
                # Amplitude perturbation quotient
                features['apq'] = np.std(amplitudes) / (np.mean(amplitudes) + 1e-10)
            
            # 2. Micro-pitch variations (not just jitter, but subtle fluctuations)
            if LIBROSA_AVAILABLE:
                # Use short-time pitch tracking
                pitches, magnitudes = librosa.piptrack(y=y, sr=sr, n_fft=512, hop_length=128)
                pitch_track = []
                for t in range(pitches.shape[1]):
                    idx = magnitudes[:, t].argmax()
                    p = pitches[idx, t]
                    if 50 < p < 500:
                        pitch_track.append(p)
                
                if len(pitch_track) > 20:
                    pitch_track = np.array(pitch_track)
                    # Compute pitch perturbation quotient
                    pitch_diff = np.abs(np.diff(pitch_track))
                    features['ppq'] = np.mean(pitch_diff) / (np.mean(pitch_track) + 1e-10)
                    
                    # Rapid pitch fluctuations (high frequency variations)
                    if len(pitch_track) > 50:
                        pitch_detrended = pitch_track - uniform_filter1d(pitch_track, size=10)
                        features['pitch_micro_var'] = np.var(pitch_detrended)
            
            # 3. Spectral micro-variations
            # Analyze frame-to-frame spectral changes at fine time resolution
            D = np.abs(librosa.stft(y, n_fft=512, hop_length=128))
            spectral_diff = np.diff(D, axis=1)
            
            # Micro spectral flux
            features['micro_spectral_flux'] = np.mean(np.sqrt(np.sum(spectral_diff**2, axis=0)))
            features['micro_spectral_flux_std'] = np.std(np.sqrt(np.sum(spectral_diff**2, axis=0)))
            
            # 4. Formant-like analysis using LPC-based approach
            # Human formants have natural variations; AI may be too consistent
            if SCIPY_AVAILABLE:
                # Use simple spectral peak analysis as formant proxy
                n_formant_frames = min(50, n_frames)
                formant_positions = []
                
                for i in range(0, len(y) - frame_length, len(y) // n_formant_frames):
                    frame = y[i:i + frame_length]
                    if len(frame) < frame_length:
                        continue
                    
                    # Compute spectrum
                    spectrum = np.abs(fft(frame * np.hanning(len(frame))))[:len(frame)//2]
                    freqs = np.fft.fftfreq(len(frame), 1/sr)[:len(frame)//2]
                    
                    # Find peaks (formant candidates)
                    peaks, _ = signal.find_peaks(spectrum, height=np.max(spectrum) * 0.1, distance=10)
                    if len(peaks) >= 2:
                        # Take first two major peaks as F1, F2 proxies
                        sorted_peaks = peaks[np.argsort(spectrum[peaks])[::-1]][:2]
                        formant_positions.append([freqs[sorted_peaks[0]], freqs[sorted_peaks[1]]])
                
                if len(formant_positions) > 5:
                    formant_positions = np.array(formant_positions)
                    features['formant_f1_var'] = np.var(formant_positions[:, 0])
                    features['formant_f2_var'] = np.var(formant_positions[:, 1])
                    features['formant_trajectory_var'] = np.var(np.diff(formant_positions, axis=0))
            
        except Exception as e:
            logger.warning(f"Micro-modulation analysis failed: {e}")
        
        return features

    def analyze_breath_patterns(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Analyze breath and pause patterns
        Human speech has natural breathing patterns that AI often lacks
        """
        features = {}
        
        try:
            # Compute RMS energy with small window for fine detail
            frame_length = int(0.02 * sr)  # 20ms
            hop_length = int(0.005 * sr)   # 5ms hop
            
            if LIBROSA_AVAILABLE:
                rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
            else:
                n_frames = (len(y) - frame_length) // hop_length + 1
                rms = np.array([np.sqrt(np.mean(y[i*hop_length:i*hop_length+frame_length]**2)) 
                               for i in range(n_frames)])
            
            # Normalize RMS
            rms_norm = rms / (np.max(rms) + 1e-10)
            
            # Find quiet regions (potential breath/pause regions)
            quiet_threshold = 0.1
            quiet_mask = rms_norm < quiet_threshold
            
            # Count transitions into and out of quiet regions
            transitions = np.diff(quiet_mask.astype(int))
            n_pauses = np.sum(transitions == 1)  # Entries into quiet
            
            # Pause statistics
            features['pause_count'] = n_pauses
            features['pause_rate'] = n_pauses / (len(y) / sr)  # Pauses per second
            
            # Analyze quiet region characteristics (potential breath sounds)
            if np.sum(quiet_mask) > 0:
                quiet_regions = rms_norm[quiet_mask]
                features['quiet_energy_mean'] = np.mean(quiet_regions)
                features['quiet_energy_var'] = np.var(quiet_regions)
                
                # In human speech, quiet regions aren't completely silent (breath sounds)
                # AI tends to have very clean silences
                features['breath_indicator'] = np.mean(quiet_regions > 0.02)
            else:
                features['quiet_energy_mean'] = 0
                features['quiet_energy_var'] = 0
                features['breath_indicator'] = 0
            
            # Analyze pause durations
            if n_pauses > 0:
                # Find pause start and end indices
                pause_starts = np.where(transitions == 1)[0]
                pause_ends = np.where(transitions == -1)[0]
                
                # Handle edge cases
                if len(pause_ends) > 0 and len(pause_starts) > 0:
                    if pause_ends[0] < pause_starts[0]:
                        pause_ends = pause_ends[1:]
                    if len(pause_starts) > len(pause_ends):
                        pause_starts = pause_starts[:len(pause_ends)]
                    
                    if len(pause_starts) > 0 and len(pause_ends) > 0:
                        pause_durations = (pause_ends - pause_starts) * (hop_length / sr)
                        features['pause_duration_mean'] = np.mean(pause_durations)
                        features['pause_duration_var'] = np.var(pause_durations)
                        features['pause_duration_cv'] = np.std(pause_durations) / (np.mean(pause_durations) + 1e-10)
                    else:
                        features['pause_duration_mean'] = 0
                        features['pause_duration_var'] = 0
                        features['pause_duration_cv'] = 0
                else:
                    features['pause_duration_mean'] = 0
                    features['pause_duration_var'] = 0
                    features['pause_duration_cv'] = 0
            else:
                features['pause_duration_mean'] = 0
                features['pause_duration_var'] = 0
                features['pause_duration_cv'] = 0
            
            # Onset detection: how does energy ramp up after pauses?
            # Human voice has more natural onsets, AI can be more abrupt
            if LIBROSA_AVAILABLE and len(y) > sr * 0.1:
                onset_env = librosa.onset.onset_strength(y=y, sr=sr)
                features['onset_strength_mean'] = np.mean(onset_env)
                features['onset_strength_var'] = np.var(onset_env)
                features['onset_strength_max'] = np.max(onset_env)
                
                # Onset regularity (AI often has more regular onsets)
                onsets = librosa.onset.onset_detect(y=y, sr=sr, units='time')
                if len(onsets) > 2:
                    onset_intervals = np.diff(onsets)
                    features['onset_interval_cv'] = np.std(onset_intervals) / (np.mean(onset_intervals) + 1e-10)
                else:
                    features['onset_interval_cv'] = 0
            
        except Exception as e:
            logger.warning(f"Breath pattern analysis failed: {e}")
        
        return features


class EnsembleClassifier:
    """
    Ensemble classifier combining multiple detection strategies
    Enhanced with research-backed thresholds for AI voice detection
    """
    
    def __init__(self):
        # Thresholds carefully tuned for AI voice detection
        # AI voices typically have: less variation, smoother transitions, more consistent patterns
        self.thresholds = {
            # === MFCC-based (HIGHEST PRIORITY - most reliable indicators) ===
            'mfcc_overall_var': {'threshold': 120, 'direction': 'below', 'weight': 3.0, 'ai_indicator': True},
            'mfcc_delta_mean': {'threshold': 6, 'direction': 'below', 'weight': 2.8, 'ai_indicator': True},
            'mfcc_delta2_mean': {'threshold': 3, 'direction': 'below', 'weight': 2.5, 'ai_indicator': True},
            'mfcc_temporal_diff_mean': {'threshold': 1.5, 'direction': 'below', 'weight': 2.5, 'ai_indicator': True},
            'mfcc_delta_std': {'threshold': 5, 'direction': 'below', 'weight': 2.2, 'ai_indicator': True},
            'mfcc_corr_offdiag_std': {'threshold': 0.3, 'direction': 'below', 'weight': 2.0, 'ai_indicator': True},
            'mfcc_0_std': {'threshold': 8, 'direction': 'below', 'weight': 1.8, 'ai_indicator': True},
            'mfcc_1_std': {'threshold': 6, 'direction': 'below', 'weight': 1.8, 'ai_indicator': True},
            'mfcc_kurtosis': {'threshold': 0, 'direction': 'below', 'weight': 1.5, 'ai_indicator': True},
            
            # === Pitch-based (HIGH PRIORITY - very discriminative) ===
            'pitch_cv': {'threshold': 0.12, 'direction': 'below', 'weight': 3.0, 'ai_indicator': True},
            'pitch_jitter': {'threshold': 0.008, 'direction': 'below', 'weight': 2.8, 'ai_indicator': True},
            'pitch_diff_std': {'threshold': 12, 'direction': 'below', 'weight': 2.5, 'ai_indicator': True},
            'pitch_diff_mean': {'threshold': 8, 'direction': 'below', 'weight': 2.3, 'ai_indicator': True},
            'pitch_range': {'threshold': 40, 'direction': 'below', 'weight': 2.0, 'ai_indicator': True},
            'pitch_iqr': {'threshold': 20, 'direction': 'below', 'weight': 1.8, 'ai_indicator': True},
            'pitch_std': {'threshold': 20, 'direction': 'below', 'weight': 1.8, 'ai_indicator': True},
            'pitch_kurtosis': {'threshold': 1, 'direction': 'below', 'weight': 1.5, 'ai_indicator': True},
            
            # === Spectral-based (MEDIUM-HIGH PRIORITY) ===
            'spectral_smoothness': {'threshold': 2.5, 'direction': 'below', 'weight': 2.2, 'ai_indicator': True},
            'spectral_flux_std': {'threshold': 3.5, 'direction': 'below', 'weight': 2.0, 'ai_indicator': True},
            'spectral_flux_mean': {'threshold': 8, 'direction': 'below', 'weight': 1.8, 'ai_indicator': True},
            'spectral_flatness_mean': {'threshold': 0.15, 'direction': 'above', 'weight': 2.0, 'ai_indicator': True},
            'spectral_flatness_std': {'threshold': 0.05, 'direction': 'below', 'weight': 1.8, 'ai_indicator': True},
            'spectral_contrast_std': {'threshold': 6, 'direction': 'below', 'weight': 1.8, 'ai_indicator': True},
            'spectral_centroid_std': {'threshold': 300, 'direction': 'below', 'weight': 1.8, 'ai_indicator': True},
            'spectral_bandwidth_std': {'threshold': 200, 'direction': 'below', 'weight': 1.6, 'ai_indicator': True},
            'spectral_rolloff_std': {'threshold': 400, 'direction': 'below', 'weight': 1.5, 'ai_indicator': True},
            'high_low_freq_ratio': {'threshold': 0.05, 'direction': 'below', 'weight': 1.5, 'ai_indicator': True},
            'band_energy_std': {'threshold': 0.003, 'direction': 'below', 'weight': 1.5, 'ai_indicator': True},
            
            # === Temporal-based (MEDIUM PRIORITY) ===
            'dynamic_range': {'threshold': 18, 'direction': 'below', 'weight': 2.0, 'ai_indicator': True},
            'rms_std': {'threshold': 0.04, 'direction': 'below', 'weight': 2.0, 'ai_indicator': True},
            'rms_range': {'threshold': 0.15, 'direction': 'below', 'weight': 1.8, 'ai_indicator': True},
            'zcr_std': {'threshold': 0.04, 'direction': 'below', 'weight': 1.8, 'ai_indicator': True},
            'zcr_range': {'threshold': 0.1, 'direction': 'below', 'weight': 1.5, 'ai_indicator': True},
            'envelope_roughness': {'threshold': 0.008, 'direction': 'below', 'weight': 2.2, 'ai_indicator': True},
            'envelope_irregularity': {'threshold': 0.05, 'direction': 'below', 'weight': 1.8, 'ai_indicator': True},
            'silence_ratio': {'threshold': 0.03, 'direction': 'below', 'weight': 1.3, 'ai_indicator': True},
            'autocorr_peak_ratio': {'threshold': 0.8, 'direction': 'above', 'weight': 1.8, 'ai_indicator': True},
            
            # === Harmonic-based (MEDIUM PRIORITY) ===
            'harmonic_percussive_ratio': {'threshold': 15, 'direction': 'above', 'weight': 1.8, 'ai_indicator': True},
            'harmonic_std': {'threshold': 0.05, 'direction': 'below', 'weight': 1.5, 'ai_indicator': True},
            
            # === Noise-based (MEDIUM PRIORITY) ===
            'residual_ratio': {'threshold': 0.03, 'direction': 'below', 'weight': 2.0, 'ai_indicator': True},
            'residual_variance': {'threshold': 0.001, 'direction': 'below', 'weight': 1.8, 'ai_indicator': True},
            'hf_noise_ratio': {'threshold': 0.0008, 'direction': 'below', 'weight': 1.8, 'ai_indicator': True},
            'snr_estimate': {'threshold': 35, 'direction': 'above', 'weight': 1.8, 'ai_indicator': True},
            
            # === Phase-based (MEDIUM PRIORITY) ===
            'phase_diff_std': {'threshold': 0.8, 'direction': 'below', 'weight': 2.0, 'ai_indicator': True},
            'phase_coherence': {'threshold': 0.7, 'direction': 'above', 'weight': 1.8, 'ai_indicator': True},
            'group_delay_std': {'threshold': 0.4, 'direction': 'below', 'weight': 1.6, 'ai_indicator': True},
            
            # === Micro-modulation (HIGH PRIORITY - very discriminative for AI vs Human) ===
            # Shimmer: amplitude variation - humans have natural shimmer, AI is too consistent
            'shimmer': {'threshold': 0.03, 'direction': 'below', 'weight': 3.0, 'ai_indicator': True},
            'shimmer_db': {'threshold': 0.25, 'direction': 'below', 'weight': 2.8, 'ai_indicator': True},
            'apq': {'threshold': 0.025, 'direction': 'below', 'weight': 2.5, 'ai_indicator': True},
            
            # Pitch perturbation quotient - human voice has micro pitch variations
            'ppq': {'threshold': 0.008, 'direction': 'below', 'weight': 3.0, 'ai_indicator': True},
            'pitch_micro_var': {'threshold': 0.5, 'direction': 'below', 'weight': 2.8, 'ai_indicator': True},
            
            # Micro spectral flux - frame-to-frame variations
            'micro_spectral_flux': {'threshold': 0.05, 'direction': 'below', 'weight': 2.5, 'ai_indicator': True},
            'micro_spectral_flux_std': {'threshold': 0.02, 'direction': 'below', 'weight': 2.2, 'ai_indicator': True},
            
            # Formant variations - human formants vary naturally
            'formant_f1_var': {'threshold': 50, 'direction': 'below', 'weight': 2.5, 'ai_indicator': True},
            'formant_f2_var': {'threshold': 80, 'direction': 'below', 'weight': 2.5, 'ai_indicator': True},
            'formant_trajectory_var': {'threshold': 0.02, 'direction': 'below', 'weight': 2.2, 'ai_indicator': True},
            
            # === Breath and Pause Patterns (HIGH PRIORITY - very discriminative) ===
            # Human speech has natural breath/pause patterns that AI lacks
            'pause_rate': {'threshold': 0.3, 'direction': 'below', 'weight': 2.2, 'ai_indicator': True},
            'breath_indicator': {'threshold': 0.1, 'direction': 'below', 'weight': 2.5, 'ai_indicator': True},
            'quiet_energy_var': {'threshold': 0.001, 'direction': 'below', 'weight': 2.0, 'ai_indicator': True},
            'pause_duration_cv': {'threshold': 0.3, 'direction': 'below', 'weight': 2.3, 'ai_indicator': True},
            'onset_strength_var': {'threshold': 1.0, 'direction': 'below', 'weight': 2.0, 'ai_indicator': True},
            'onset_interval_cv': {'threshold': 0.4, 'direction': 'below', 'weight': 2.5, 'ai_indicator': True},
            
            # === Statistical (LOWER PRIORITY - supporting evidence) ===
            'signal_kurtosis': {'threshold': 4, 'direction': 'below', 'weight': 1.3, 'ai_indicator': True},
            'signal_skewness': {'threshold': 0.3, 'direction': 'below', 'weight': 1.0, 'ai_indicator': True},
            'crest_factor': {'threshold': 2.5, 'direction': 'below', 'weight': 1.2, 'ai_indicator': True},
            'hist_entropy': {'threshold': 4, 'direction': 'below', 'weight': 1.3, 'ai_indicator': True},
            'signal_iqr': {'threshold': 0.1, 'direction': 'below', 'weight': 1.0, 'ai_indicator': True},
        }
    
    def classify(self, features: Dict[str, float]) -> Tuple[str, float, Dict]:
        """
        Classify based on ensemble of feature thresholds with soft voting
        Uses distance from threshold to weight votes more precisely
        """
        ai_score = 0.0
        human_score = 0.0
        total_weight = 0.0
        vote_details = {}
        matched_features = 0
        
        for feature_name, config in self.thresholds.items():
            if feature_name not in features:
                continue
            
            matched_features += 1
            value = features[feature_name]
            threshold = config['threshold']
            direction = config['direction']
            weight = config['weight']
            ai_indicator = config['ai_indicator']
            
            # Calculate how far from threshold (normalized distance)
            if direction == 'below':
                # AI if value < threshold
                if threshold != 0:
                    distance = (threshold - value) / abs(threshold)
                else:
                    distance = -value if value > 0 else 1
                indicates_ai = value < threshold
            else:
                # AI if value > threshold
                if threshold != 0:
                    distance = (value - threshold) / abs(threshold)
                else:
                    distance = value if value > 0 else -1
                indicates_ai = value > threshold
            
            # Apply indicator logic
            if not ai_indicator:
                indicates_ai = not indicates_ai
                distance = -distance
            
            # Soft voting: use sigmoid-like scaling for distance
            # This gives stronger votes when far from threshold
            confidence_factor = min(2.0, max(0.1, 1.0 + np.tanh(distance * 0.5)))
            effective_weight = weight * confidence_factor
            
            # Cast vote with weighted confidence
            if indicates_ai:
                ai_score += effective_weight
                vote_details[feature_name] = {'value': round(value, 4), 'threshold': threshold, 'vote': 'AI', 'weight': round(effective_weight, 3), 'distance': round(distance, 3)}
            else:
                human_score += effective_weight
                vote_details[feature_name] = {'value': round(value, 4), 'threshold': threshold, 'vote': 'HUMAN', 'weight': round(effective_weight, 3), 'distance': round(distance, 3)}
            
            total_weight += effective_weight
        
        # Require minimum features for reliable classification
        if matched_features < 5:
            logger.warning(f"Only {matched_features} features matched, using fallback")
            return "HUMAN", 0.55, vote_details
        
        # Calculate final score
        if total_weight > 0:
            ai_probability = ai_score / total_weight
        else:
            ai_probability = 0.5
        
        # Log voting summary
        ai_vote_count = sum(1 for v in vote_details.values() if v['vote'] == 'AI')
        human_vote_count = sum(1 for v in vote_details.values() if v['vote'] == 'HUMAN')
        logger.info(f"Feature votes: AI={ai_vote_count}, HUMAN={human_vote_count}, AI_prob={ai_probability:.3f}")
        
        # Also consider raw vote ratio (gives equal weight to each feature type)
        raw_ai_ratio = ai_vote_count / max(1, ai_vote_count + human_vote_count)
        
        # Combine weighted probability with raw vote ratio for balanced decision
        # This prevents high-weight features from dominating the decision
        combined_ai_prob = 0.6 * ai_probability + 0.4 * raw_ai_ratio
        logger.info(f"Weighted AI prob: {ai_probability:.3f}, Raw vote ratio: {raw_ai_ratio:.3f}, Combined: {combined_ai_prob:.3f}")
        
        # Classification with adaptive threshold
        decision_threshold = 0.50  # Use 0.5 for balanced decision
        
        if combined_ai_prob >= decision_threshold:
            classification = "AI_GENERATED"
            # Map [0.50, 1.0] -> [0.52, 0.98]
            confidence = 0.52 + (combined_ai_prob - decision_threshold) * (0.98 - 0.52) / (1.0 - decision_threshold)
        else:
            classification = "HUMAN"
            # Map [0.0, 0.50] -> [0.98, 0.52]
            confidence = 0.98 - (combined_ai_prob / decision_threshold) * (0.98 - 0.52)
        
        # Ensure confidence is in valid range and reflects certainty
        confidence = min(0.98, max(0.52, confidence))
        
        # Boost confidence if vote is very one-sided
        vote_ratio = max(ai_vote_count, human_vote_count) / max(1, ai_vote_count + human_vote_count)
        if vote_ratio > 0.75:
            confidence = min(0.98, confidence * 1.05)
        
        return classification, round(confidence, 4), vote_details


def detect_ai_voice(
    audio_data: bytes,
    language: str
) -> Tuple[Literal["AI_GENERATED", "HUMAN"], float]:
    """
    Main detection function - uses advanced multi-technique analysis
    """
    logger.info(f"Starting advanced AI voice detection for {len(audio_data)} bytes, language: {language}")
    
    try:
        # Initialize analyzer
        analyzer = AdvancedVoiceAnalyzer()
        
        # Load audio
        try:
            y, sr = analyzer.load_audio(audio_data)
            logger.info(f"Audio loaded: {len(y)} samples at {sr}Hz ({len(y)/sr:.2f} seconds)")
        except Exception as e:
            logger.error(f"Failed to load audio: {e}")
            # Return uncertain result
            return "HUMAN", 0.55
        
        # Check minimum audio length
        if len(y) < sr * 0.5:  # Less than 0.5 seconds
            logger.warning("Audio too short for reliable analysis")
            return "HUMAN", 0.55
        
        # Normalize audio
        y = librosa.util.normalize(y)
        
        # Extract all features
        all_features = {}
        
        # 1. Spectral artifacts
        logger.info("Analyzing spectral artifacts...")
        spectral_features = analyzer.analyze_spectral_artifacts(y, sr)
        all_features.update(spectral_features)
        logger.info(f"Extracted {len(spectral_features)} spectral features")
        
        # 2. Temporal patterns
        logger.info("Analyzing temporal patterns...")
        temporal_features = analyzer.analyze_temporal_patterns(y, sr)
        all_features.update(temporal_features)
        logger.info(f"Extracted {len(temporal_features)} temporal features")
        
        # 3. MFCC patterns
        logger.info("Analyzing MFCC patterns...")
        mfcc_features = analyzer.analyze_mfcc_patterns(y, sr)
        all_features.update(mfcc_features)
        logger.info(f"Extracted {len(mfcc_features)} MFCC features")
        
        # 4. Pitch and prosody
        logger.info("Analyzing pitch and prosody...")
        pitch_features = analyzer.analyze_pitch_and_prosody(y, sr)
        all_features.update(pitch_features)
        logger.info(f"Extracted {len(pitch_features)} pitch features")
        
        # 5. Phase patterns
        logger.info("Analyzing phase patterns...")
        phase_features = analyzer.analyze_phase_patterns(y, sr)
        all_features.update(phase_features)
        logger.info(f"Extracted {len(phase_features)} phase features")
        
        # 6. Noise patterns
        logger.info("Analyzing noise patterns...")
        noise_features = analyzer.analyze_noise_patterns(y, sr)
        all_features.update(noise_features)
        logger.info(f"Extracted {len(noise_features)} noise features")
        
        # 7. Statistical moments
        logger.info("Analyzing statistical moments...")
        stat_features = analyzer.analyze_statistical_moments(y, sr)
        all_features.update(stat_features)
        logger.info(f"Extracted {len(stat_features)} statistical features")
        
        # 8. Micro-modulations (shimmer, jitter, formants)
        logger.info("Analyzing micro-modulations...")
        micro_features = analyzer.analyze_micro_modulations(y, sr)
        all_features.update(micro_features)
        logger.info(f"Extracted {len(micro_features)} micro-modulation features")
        
        # 9. Breath patterns (pauses, onsets, breath sounds)
        logger.info("Analyzing breath patterns...")
        breath_features = analyzer.analyze_breath_patterns(y, sr)
        all_features.update(breath_features)
        logger.info(f"Extracted {len(breath_features)} breath pattern features")
        
        logger.info(f"Total features extracted: {len(all_features)}")
        
        # Classify using ensemble
        classifier = EnsembleClassifier()
        classification, confidence, vote_details = classifier.classify(all_features)
        
        # Log key voting results
        ai_votes = sum(1 for v in vote_details.values() if v['vote'] == 'AI')
        human_votes = sum(1 for v in vote_details.values() if v['vote'] == 'HUMAN')
        logger.info(f"Voting results: AI={ai_votes}, HUMAN={human_votes}")
        logger.info(f"Final classification: {classification} with confidence {confidence:.4f}")
        
        return classification, confidence
        
    except Exception as e:
        logger.error(f"Detection failed with error: {e}", exc_info=True)
        # Return uncertain result on failure
        return "HUMAN", 0.55
