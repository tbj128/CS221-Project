from setuptools import setup

setup(
    name='CS221 Final Project',
    version='0.1.0',
    description="",
    long_description=(open('README.md').read()),
    url='https://github.com/tbj128/CS221-Project',
    install_requires=[
        'scikit-learn>=0.21.3',
        'scipy',
        'scikit-bio',
        'keras',
        'tensorflow>=2.0'
    ],
    license='MIT',
    author='Tom Jin',
    author_email='',
    packages=['src'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    zip_safe=False,
)
