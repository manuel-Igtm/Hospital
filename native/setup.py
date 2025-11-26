from setuptools import setup, Extension  # type: ignore[import-not-found]
import os
import subprocess

# Build C libraries first
native_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(native_dir, 'build')

if not os.path.exists(build_dir):
    os.makedirs(build_dir)
    subprocess.check_call(['cmake', '..'], cwd=build_dir)
    subprocess.check_call(['make'], cwd=build_dir)

# Python extensions
# Note: Only _cutils and _hl7val are implemented for now
# _authz and _bill extensions to be added later
extensions = [
    Extension(
        'hospital_native._cutils',
        sources=['python/_cutils.c'],
        include_dirs=['include', '/usr/include'],
        library_dirs=['build'],
        libraries=['cutils', 'ssl', 'crypto'],
        extra_compile_args=['-O3', '-fPIC'],
    ),
    Extension(
        'hospital_native._hl7val',
        sources=['python/_hl7val.c'],
        include_dirs=['include'],
        library_dirs=['build'],
        libraries=['hl7val'],
        extra_compile_args=['-O3', '-fPIC'],
    ),
    # TODO: Add _authz and _bill extensions when ready
    # Extension(
    #     'hospital_native._authz',
    #     sources=['python/_authz.c'],
    #     include_dirs=['include'],
    #     library_dirs=['build'],
    #     libraries=['authz'],
    #     extra_compile_args=['-O3', '-fPIC'],
    # ),
    # Extension(
    #     'hospital_native._bill',
    #     sources=['python/_bill.c'],
    #     include_dirs=['include'],
    #     library_dirs=['build'],
    #     libraries=['bill'],
    #     extra_compile_args=['-O3', '-fPIC'],
    # ),
]

setup(
    name='hospital-native',
    version='0.1.0',
    ext_modules=extensions,
    packages=['hospital_native'],
    package_dir={'hospital_native': 'python'},
)
