from setuptools import setup

setup(
    name="kubepi",
    version="0.1",
    packages=["kubepi", "kubepi.commands", "kubepi.helpers"],
    include_package_data=True,
    install_requires=["click==7.1.1",
                      "click-log==0.3.2",
                      "click-spinner==0.1.8",
                      "docker==4.2.0",
                      "gitpython==3.1.1",
                      "paramiko>=2.7.1",
                      "semver>=2.9.1",
                      "cryptography>=2.9.1"],
    entry_points="""
        [console_scripts]
        kubepi=kubepi.cli:cli
    """,
)
