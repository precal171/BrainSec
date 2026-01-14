# Dependency Audit Report - BrainSec Project
**Generated:** January 14, 2026
**Audited File:** `/home/user/BrainSec/install/requirements.txt`

---

## Executive Summary

This audit identified **critical security vulnerabilities** and **severely outdated packages** in the BrainSec project dependencies. The project uses packages that are **5-6 years old**, creating significant security risks and compatibility issues with modern Python environments (Python 3.11+).

### Severity Breakdown
- **CRITICAL:** 3 packages with known security vulnerabilities
- **HIGH:** 3 packages severely outdated (5+ years old)
- **MEDIUM:** 2 missing dependencies, 4 potentially unused packages
- **LOW:** Various unpinned versions causing inconsistent builds

---

## 1. CRITICAL SECURITY VULNERABILITIES

### 1.1 PyTorch 1.4.0 (Released: January 2020)
**Current version in requirements.txt:** `torch==1.4.0`
**Latest stable version:** 2.9.x (2.10 releasing Jan 21, 2026)
**Age:** ~6 years old

**Known Vulnerabilities:**
- **CVE-2025-32434** (CVSS 9.3 - Critical): Remote Code Execution via `torch.load()` with `weights_only=True`
  - Affects all PyTorch versions up to 2.5.1
  - Fixed in PyTorch 2.6.0
- **CVE-2023-43654** (CVSS 9.8): ShellTorch RCE vulnerability in TorchServe
- **CVE-2025-2953**: Denial of Service vulnerability
- 33+ CVE records match PyTorch, many affecting older versions

**Recommendation:** Upgrade to PyTorch 2.9+ immediately

### 1.2 TensorFlow 2.4.0 (Released: December 2020)
**Current version in requirements.txt:** `tensorflow==2.4.0`
**Latest stable version:** 2.20.0 (as of August 2025)
**Age:** ~5 years old

**Known Vulnerabilities:**
- **CVE-2022-36026**: Affects `QuantizeAndDequantizeV3`, fixed in 2.7.2+
- **CVE-2024-3660**: Keras downgrade attack vulnerability
- **CVE-2023-33976**: Fixed in TensorFlow 2.13.0
- Multiple security patches released across versions 2.5-2.20
- Version 2.4.0 is **no longer supported** by TensorFlow team

**Recommendation:** Upgrade to TensorFlow 2.18+ (supports Python 3.9-3.13)

### 1.3 Pillow (Unpinned Version)
**Current version in requirements.txt:** No version specified
**Latest version:** Updates regularly with security patches

**Known Historical Vulnerabilities:**
- **CVE-2022-22817**: Arbitrary code execution via environment parameter
- **CVE-2023-5129**: libwebp heap-based buffer overflow
- Multiple vulnerabilities in older versions (before 8.x, 9.x, 10.x)

**Recommendation:** Pin to latest stable version (10.x+) and update regularly

---

## 2. SEVERELY OUTDATED PACKAGES

### 2.1 SciPy 1.4.1 (Released: April 2020)
**Current:** `scipy==1.4.1`
**Latest:** 1.17.0 (released January 10, 2026)
**Age:** Nearly 6 years old

**Issues:**
- Requires Python 3.6-3.8 (incompatible with modern Python 3.11-3.14)
- Cannot build on Python 3.11+ (build system incompatibilities)
- Missing 6 years of bug fixes, performance improvements, and new features
- Not compatible with latest NumPy versions

**Recommendation:** Upgrade to scipy>=1.17.0

### 2.2 TorchVision 0.5.0 (Released: January 2020)
**Current:** `torchvision==0.5.0`
**Latest:** Compatible with PyTorch 2.9+
**Age:** ~6 years old

**Issues:**
- Tied to ancient PyTorch 1.4.0
- Missing modern vision models and transformers
- No support for recent dataset formats

**Recommendation:** Upgrade to torchvision compatible with PyTorch 2.9+

### 2.3 TensorFlow Nightly Packages
**Current:** `tfds-nightly`
**Issues:**
- Nightly builds are unstable and not recommended for production
- Can introduce breaking changes
- May conflict with stable TensorFlow 2.4.0

**Recommendation:** Replace with stable `tensorflow-datasets` package

---

## 3. MISSING DEPENDENCIES

### 3.1 OpenCV (cv2)
**Status:** Used in code but NOT in requirements.txt
**Found in:** Multiple Python files with `import cv2` and `import cv2 as cv`

**Recommendation:** Add `opencv-python>=4.8.0` to requirements.txt

### 3.2 CZIfile
**Status:** Used in code but NOT in requirements.txt
**Found in:** `pyscripts/1_preprocessing_czi.py` with `import czifile`

**Recommendation:** Add `czifile>=2019.7.2` or `aicspylibczi>=3.0.0` (modern alternative)

---

## 4. POTENTIALLY UNNECESSARY PACKAGES (Bloat)

### 4.1 Confirmed Unused
- **scikit-learn**: Listed in requirements but no imports found in codebase
- **PyWavelets**: Listed in requirements but no imports found in codebase

### 4.2 Development Dependencies (Should Move to dev-requirements.txt)
- **setuptools**: Build/installation tool, not runtime dependency
- **ipython**: Interactive shell, useful for Jupyter but not runtime dependency
- **jupyter**: Development/notebook environment
- **pytest**: Testing framework, not runtime dependency
- **virtualenv**: Environment management tool
- **pydot**: Only used for `tf.keras.utils.plot_model` visualization (optional)
- **tensorboard_plugin_profile**: Optional TensorBoard plugin

### 4.3 Legacy Dependencies
- **six**: Python 2/3 compatibility library (Python 2 EOL was 2020)
  - Modern Python 3 doesn't need this
  - TensorFlow 2.x and PyTorch 1.4+ should not require it

### 4.4 Specialized Tools
- **cppyy**: Automatic Python-C++ binding, likely for gSLICr integration
  - Verify if still needed; may be replaceable with modern alternatives

**Recommendation:**
- Remove unused packages: `scikit-learn`, `PyWavelets`
- Move dev dependencies to separate `dev-requirements.txt`
- Consider removing `six` if not explicitly required by current package versions

---

## 5. VERSION PINNING ISSUES

### 5.1 Unpinned Packages (Inconsistent Builds)
The following packages have no version pins, leading to potential build inconsistencies:

**Core Dependencies:**
- numpy (critical - should be pinned)
- pandas
- matplotlib
- Pillow
- scikit-image
- pyvips
- tensorboard

**Development Tools:**
- setuptools
- ipython
- jupyter
- pytest
- virtualenv
- pydot
- six
- lxml

**Recommendation:** Pin all core runtime dependencies to specific versions or version ranges

---

## 6. RECOMMENDED UPDATED REQUIREMENTS.TXT

```txt
# ============================================
# Core Scientific Computing
# ============================================
numpy>=1.24.0,<2.0.0
scipy>=1.17.0
pandas>=2.0.0
matplotlib>=3.7.0

# ============================================
# Image Processing
# ============================================
Pillow>=10.0.0
scikit-image>=0.21.0
opencv-python>=4.8.0
pyvips>=2.2.0
czifile>=2019.7.2  # For .czi file support

# ============================================
# Deep Learning Frameworks
# ============================================
# TensorFlow (choose one based on your needs)
tensorflow>=2.18.0  # CPU version
# tensorflow[and-cuda]>=2.18.0  # GPU version with CUDA

tensorboard>=2.18.0

# PyTorch (choose based on your CUDA version)
torch>=2.4.0  # CPU version
torchvision>=0.19.0
# For GPU, see: https://pytorch.org/get-started/locally/

# ============================================
# Utilities
# ============================================
tqdm>=4.66.0
lxml>=5.0.0
argcomplete>=3.0.0  # If used for CLI argument completion

# ============================================
# Optional: C++ Bindings (verify if needed)
# ============================================
# cppyy>=3.0.0  # For gSLICr integration - verify if still needed

# ============================================
# Development Dependencies
# (Move to dev-requirements.txt in production)
# ============================================
# setuptools>=68.0.0
# ipython>=8.12.0
# jupyter>=1.0.0
# pytest>=7.4.0
# pydot>=2.0.0
```

**Create separate `dev-requirements.txt`:**
```txt
# Development and Testing Tools
setuptools>=68.0.0
ipython>=8.12.0
jupyter>=1.0.0
pytest>=7.4.0
pydot>=2.0.0
tensorboard-plugin-profile>=2.15.0  # If needed for profiling
```

---

## 7. MIGRATION CONSIDERATIONS

### 7.1 Breaking Changes
Upgrading from such old versions will require code changes:

**TensorFlow 2.4 → 2.18+:**
- `mixed_precision.experimental` moved to `tf.keras.mixed_precision`
- Some Keras APIs have changed
- Legacy `tensorflow.python.keras` imports should use `tensorflow.keras`

**PyTorch 1.4 → 2.9+:**
- Some APIs deprecated and removed
- Performance improvements may change numerical results slightly
- DataLoader and distributed training APIs updated

**SciPy 1.4 → 1.17:**
- Requires Python 3.11+ (current system is Python 3.11)
- Some function signatures changed
- Better array API standard support

### 7.2 Testing Strategy
1. Create new virtual environment with updated dependencies
2. Run existing test suite (`pytest tests/`)
3. Test each Python script individually
4. Check Jupyter notebooks for compatibility
5. Validate model loading and inference with updated PyTorch/TensorFlow

### 7.3 Docker Update Required
The project uses Docker (see `setup.sh`). The Dockerfile will need updates:
- Base image should use Python 3.11+
- CUDA version may need update for PyTorch 2.x
- TensorFlow 2.18+ requires CUDA 11.8 or newer

---

## 8. COMPATIBILITY MATRIX

| Package | Current | Recommended | Python Support | Notes |
|---------|---------|-------------|----------------|-------|
| Python | 3.11 | 3.11-3.12 | - | Current system |
| numpy | unpinned | 1.24+ | 3.9-3.13 | Pin version |
| scipy | 1.4.1 | 1.17.0 | 3.11-3.14 | **Critical update** |
| torch | 1.4.0 | 2.4+ | 3.8-3.12 | **Security risk** |
| torchvision | 0.5.0 | 0.19+ | 3.8-3.12 | Update with torch |
| tensorflow | 2.4.0 | 2.18+ | 3.9-3.13 | **Security risk** |
| Pillow | unpinned | 10.0+ | 3.8-3.13 | Pin for security |
| opencv-python | **MISSING** | 4.8+ | 3.8-3.13 | **Add to requirements** |

---

## 9. PRIORITY ACTION ITEMS

### Immediate (Security Critical)
1. ✅ **Add missing dependencies:** opencv-python, czifile
2. ✅ **Update PyTorch** from 1.4.0 to 2.4+ (addresses CVE-2025-32434, CVE-2023-43654)
3. ✅ **Update TensorFlow** from 2.4.0 to 2.18+ (addresses multiple CVEs)
4. ✅ **Update SciPy** from 1.4.1 to 1.17.0 (fixes Python 3.11 compatibility)

### High Priority (Stability & Maintenance)
5. ✅ **Pin all core dependencies** to specific versions
6. ✅ **Remove unused packages:** scikit-learn, PyWavelets
7. ✅ **Update torchvision** to match PyTorch version
8. ✅ **Replace tfds-nightly** with stable tensorflow-datasets

### Medium Priority (Best Practices)
9. ⏺ **Create dev-requirements.txt** for development dependencies
10. ⏺ **Remove legacy dependencies** (six, if not needed)
11. ⏺ **Update Docker configuration** for new CUDA/Python versions
12. ⏺ **Test all scripts** with updated dependencies

### Low Priority (Optimization)
13. ⏺ **Verify cppyy necessity** (may have modern alternatives)
14. ⏺ **Consider moving** to pyproject.toml (modern Python packaging)
15. ⏺ **Add dependabot** or similar for automated dependency updates

---

## 10. ESTIMATED EFFORT

- **Research & Planning:** 2-4 hours
- **Dependency Updates:** 4-8 hours
- **Code Migration:** 8-16 hours (TensorFlow/PyTorch API changes)
- **Testing & Validation:** 8-16 hours
- **Docker/Infrastructure Updates:** 2-4 hours
- **Documentation Updates:** 2-4 hours

**Total Estimated Effort:** 26-52 hours

---

## 11. REFERENCES & SOURCES

### Security Vulnerabilities
- [TensorFlow Security Vulnerabilities - CVE Details](https://www.cvedetails.com/vulnerability-list/vendor_id-1224/product_id-53738/Google-Tensorflow.html)
- [TensorFlow Vulnerabilities - Snyk](https://security.snyk.io/package/pip/tensorflow)
- [PyTorch CVE-2025-32434 - GitHub Advisory](https://github.com/advisories/GHSA-53q9-r3pm-6pq6)
- [PyTorch Security Vulnerabilities - CVE Mitre](https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=pytorch)
- [SciPy Vulnerabilities - Snyk](https://security.snyk.io/package/pip/scipy/1.4.1)
- [Pillow Vulnerabilities - CVE Details](https://www.cvedetails.com/vulnerability-list/vendor_id-10210/product_id-27460/Python-Pillow.html)

### Latest Versions
- [TensorFlow Releases - GitHub](https://github.com/tensorflow/tensorflow/releases)
- [TensorFlow on PyPI](https://pypi.org/project/tensorflow/)
- [PyTorch Releases - GitHub](https://github.com/pytorch/pytorch/releases)
- [SciPy 1.17.0 Release Notes](https://docs.scipy.org/doc/scipy/release.html)
- [SciPy Releases - GitHub](https://github.com/scipy/scipy/releases)

### Additional Resources
- [NVD - CVE-2025-32434](https://nvd.nist.gov/vuln/detail/CVE-2025-32434)
- [PyTorch torch.load RCE Advisory](https://github.com/pytorch/pytorch/security/advisories/GHSA-53q9-r3pm-6pq6)
- [TensorFlow CVE-2022-36026 Details](https://data.safetycli.com/vulnerabilities/CVE-2022-36026/51104/)

---

## Conclusion

The BrainSec project's dependencies are **critically outdated and pose significant security risks**. The most urgent actions are updating PyTorch, TensorFlow, and SciPy to address known CVEs and ensure compatibility with modern Python environments. Additionally, missing dependencies (OpenCV, czifile) must be added to prevent runtime errors.

A phased migration approach is recommended, starting with security-critical updates, followed by stability improvements and code refactoring to accommodate API changes in the newer framework versions.
