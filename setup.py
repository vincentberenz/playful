from setuptools import setup, find_packages, Extension

setup( name='playful',
       version='1.02',
       description='an interpreter for reactive programming',
       long_description="see https://github.com/vincentberenz/playful",
       packages=['playful',
                 'playful/component',
                 'playful/api',
                 'playful/display',
                 'playful/engine',
                 'playful/interpreter',
                 'playful/memory',
                 'playful/orchestration',
                 'playful/resources',
                 'playful/terminal'],
       install_requires=['funcsigs'],
       zip_safe=True,
       scripts=['playful/terminal/playful']
)
