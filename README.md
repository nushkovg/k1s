<div align="center">
<p>
  <img src="https://raw.githubusercontent.com/nushkovg/k1s-website/master/_media/logo-large.svg" />
</p>
<img alt="Travis (.org)" src="https://img.shields.io/travis/nushkovg/k1s">
<img alt="GitHub tag (latest by date)" src="https://img.shields.io/github/v/tag/nushkovg/k1s?label=version">
<img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/nushkovg/k1s">
<img alt="GitHub issues" src="https://img.shields.io/github/issues/nushkovg/k1s">
<img alt="GitHub closed pull requests" src="https://img.shields.io/github/issues-pr-closed/nushkovg/k1s">
<img alt="Website" src="https://img.shields.io/website?url=https%3A%2F%2Fwww.k1s.dev">
<img alt="GitHub" src="https://img.shields.io/github/license/nushkovg/k1s">
</div>

---

The k1s platform contains all services required to start a k3d cluster on a Raspberry PI with Skaffold. It is meant for those who want to create their own home lab cluster with a lightweight Kubernetes release with a preloaded ingress controller and several monitoring tools. Since k1s is in the early stage of development, it currently allows only [Namesilo](https://www.namesilo.com/) as the DNS provider.

## Installation

Please follow this documentation from start to finish if you want to set k1s up on your Raspberry PI. It is still in the early development phase and unexpected bugs might occur if you skip some of the steps.

You can find the documentation on the official [website](https://www.k1s.dev/).

## Features

k1s comes preloaded with the following:

- K3D
- Klipper ServiceLB
- Metrics Server
- Skaffold
- Traefik
- Prometheus
- Grafana
- Kubernetes Dashboard
- Hugo Dashboard UI
- GitHub Oauth2 Middleware
- Custom Error Pages Middleware
- Wildcard LetsEncrypt SSL Certificate
- DDNS Update CronJob for Namesilo A Records

The most of the setup is done via a CLI interface named [KubePI](https://github.com/nushkovg/kubepi). It is a custom tool for making the k1s management easier for the K3D setup, dependencies, submodules, and more. The usage of `kubepi` is explained in the documentation.

## Contributing

Please read [CONTRIBUTING.md](https://github.com/nushkovg/k1s/blob/master/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/nushkovg/k1s/tags).

## Authors

- [**Goran Nushkov**](https://github.com/nushkovg)

## License

This project is licensed under the Apache v2 License - see the [LICENSE.md](https://github.com/nushkovg/k1s/blob/master/LICENSE) file for details.

## Acknowledgments

- [vikaspogu.dev](https://vikaspogu.dev/posts/kubernetes-home-cluster-traefik/) - DNS, Routing, and CronJobs

- [thomseddon](https://github.com/thomseddon/traefik-forward-auth) - Oauth2

- [gesquive](https://github.com/gesquive/slate) - Dashboard Theme

- [tarampampam](https://github.com/tarampampam/error-pages) - Custom Traefik Error Pages
