# K1S Platform

This repository contains all services required to start a k3d cluster on a Raspberry PI with Skaffold. It is meant for those who want to create their own
HomeLab cluster with a lightweight Kubernetes release with a preloaded ingress controller and several monitoring tools. Since k1s is in the early stage of development, it currently allows only Namesilo as the DNS provider.

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

The most of the setup is done via a CLI interface named [KubePI](https://github.com/nushkovg/kubepi). It is a custom tool for making the k1s management easier for the K3D setup, dependencies, submodules, and more. The usage of `kubepi` will be explained in more detail in the following sections.

## Getting Ready

First of all, you will need a domain bought from Namesilo. As mentioned previously, it is the only supported DNS registrar in this early release of k1s. They have really cheap domains, and you can get one for as low as one dollar. New DNS registrar options will come in the next releases, but for now you can only use Namesilo.

### DNS Records

You need to prepare the DNS records once you've gotten your domain. Follow these steps to do this:

- Log into your [Namesilo](https://www.namesilo.com/) account
- Go to the [Account domains](https://www.namesilo.com/account_domains.php) page
- Select your domain from the list
- Select **Update** on the **DNS Records** field from the Domain Console list
- Create the DNS records

Here is the list of the required records:

| HOSTNAME   | TYPE  | ADDRESS/VALUE      | DISTANCE/PRIO | TTL  | SERVICE   |
|------------|-------|--------------------|---------------|------|-----------|
|            | A     | <YOUR_EXTERNAL_IP> | NA            | 3603 | 3rd-party |
| www        | CNAME | example.com        | NA            | 3603 | 3rd-party |
| traefik    | CNAME | example.com        | NA            | 3603 | 3rd-party |
| oauth      | CNAME | example.com        | NA            | 3603 | 3rd-party |
| grafana    | CNAME | example.com        | NA            | 3603 | 3rd-party |
| kube       | CNAME | example.com        | NA            | 3603 | 3rd-party |
| prometheus | CNAME | example.com        | NA            | 3603 | 3rd-party |

Make sure to replace <YOUR_EXTERNAL_IP> with your external IP address. You can find it out via [WhatIsMyIP](https://www.whatismyip.com/). Also replace the `example.com` with your own domain.

The DDNS CronJob which is integrated into k1s will take care of updating the IP address of the A record each time it changes (in case of a dynamic IP), so you won't have to do it manually.

### Router Port Forwarding

After making sure that you have a domain registered, you have to open port `:80` and port `:443` on your network by using the port forwarding option on your router. Since there are many different routers out there, you must find out for yourself about how to do this on your own router.

You can check if the ports are open [here](https://www.canyouseeme.org/).

After getting a domain and opening the required ports, you can continue with this guide.

### SSH Access

Everything you see below should be done on your RaspberryPI, via `ssh` or directly. To enable SSH access to your RaspberryPI, see the [official tutorial](https://www.raspberrypi.org/documentation/remote-access/ssh/).

It is recommmended to set a static IP address on the RaspberryPI for easier access. To set a static IP, do the following:

```bash
# Get the IPv4 address of the Raspberry
ip route get 1.2.3.4 | awk '{print $7}'
# Edit /etc/dhcpcd.conf
sudo nano /etc/dhcpcd.conf
# Modify the following lines (uncomment if necessary)
interface eth0
static ip_address=<YOUR_IPV4_ADDRESS>/24
static routers=192.168.0.1 # or 192.168.1.1 depending on your IPv4
static domain_name_servers=1.1.1.1
```

Save the modified file and restart your RaspberryPI. Check if the changes are saved by running the `ip route get 1.2.3.4 | awk '{print $7}'` command again on your RaspberryPI.

After this, it is recommended to set an alias on your host machine for easier SSH access. Place this in your `.bashrc` or `.zshrc`:

```bash
alias pi="ssh pi@<YOUR_IPV4_ADDRESS>"
```

Save and run `source ~/.bashrc` or `source ~/.zshrc` to reload the configuration. Now you will be able to SSH into your RaspberryPI by simply running `pi` on your host machine. To be able to log into your RaspberryPI without the need for a password, see the [official passwordless SSH guide](https://www.raspberrypi.org/documentation/remote-access/ssh/passwordless.md).

> **_NOTE:_** If you are using `termite` as the terminal on your host machine, you might experience issues while SSH-ing. Place this line in the `~/.bashrc` or `~/.zshrc` file on you RaspberryPI: `export TERM=termite`.

### Dependencies

You will need the following packages installed on your RaspberryPI:

- git
- go
- docker
- python3-pip

#### **Raspberry Pi OS (Raspbian)**

```bash
sudo apt-get install python3-pip git docker.io golang-go
```

#### **Arch**

```bash
sudo pacman -Syu python3-pip git docker go
```

#### **Docker Setup**

Add your user to the `docker` group and log-off/log-on from your X session, reboot, or just type in `newgrp docker`.

```bash
sudo usermod -aG docker $USER
```

#### **Clone K1S**

```bash
git clone git@github.com:nushkovg/k1s.git
cd k1s
```

## KubePI

For easier usage and setup there is a CLI called [KubePI](https://github.com/nushkovg/kubepi). It is a custom tool for making the k1s management easier for the K3D setup, dependencies, submodules, and more. It needs at least Python 3.7. Please check that you have Python 3.7 or later by running:

```bash
# Raspberry Pi OS (Raspbian) users
python3 --version
# Arch users
python --version
```

If you are not running Python 3.7 or later, please upgrade your Python version.

[KubePI](https://github.com/nushkovg/kubepi) is available as an official [PyPI package](https://pypi.org/project/kubepi/). Follow these steps to install `kubepi` by using `pip`:

```bash
# Raspberry Pi OS (Raspbian) still shipping python2 by default
pip3 install kubepi
# Arch shipping python3 by default
pip install kubepi
```

Now you should have the `kubepi` command in your path and you can run `kubepi` to display the help:

```bash
pi@k1s:~$ kubepi
Usage: kubepi [OPTIONS] COMMAND [ARGS]...

  Kubepi CLI for easier k3d setup on Raspberry PI.

Options:
  --kube-context TEXT  The kubernetes context to use
  -v, --verbosity LVL  Either CRITICAL, ERROR, WARNING, INFO or DEBUG
  --help               Show this message and exit.

Commands:
  apps       App commands
  k3d        Manage k3d clusters
  platform   Platform commands
  preflight  Preflight checks
  setup      Setup infrastructure services
```

To see the options of each command, just run:

```bash
kubepi <COMMAND> --help
```

For example:

```bash
pi@k1s:~$ kubepi k3d --help
Usage: kubepi k3d [OPTIONS] COMMAND [ARGS]...

  Manage k3d clusters. The name of the cluster is taken from the option
  --kube-context which defaults to 'k1s'

Options:
  --help  Show this message and exit.

Commands:
  create  Create cluster
  delete  Delete cluster
  start   Start cluster
  status  Cluster status
  stop    Stop cluster
```

## Installing K1S

### Tools Setup

The platform uses the following tools. They can be automatically installed with `kubepi`:

- kubectl
- helm
- k3d
- skaffold

Use `kubepi` to initialize the toolchain. The command below will download all necessary tools and store them in the `./bin` directory. Make sure you are in the root of the cloned git repository and run:

```bash
kubepi setup init
```

Follow the instructions prompted to add the bin/ directory to your PATH. Make sure to log-off/log-on once you have done so. If you don't want to do that, simply run `source ~/.profile`, `source ~/.bashrc` or `source ~/.zshrc`.

> **_NOTE:_** The command will tell you to place the directory in your PATH by placing it in the `~/.profile` file. If for some reason this does not work, replace `~/.profile` with `~/.bashrc` or `~/.zshrc` in the `echo export PATH=<K1S_DIRECTORY>/bin:$PATH >> ~/.profile` command and run `source ~/.bashrc` or `source ~/.zshrc` again.

### Environment Setup

Make sure that you are in the root of the repository. There are certain defaults that are in use:

- The default context is set to **k1s**
- The k3d cluster is created and sets the kube-context to **k1s**
- **k1s** namespace is created
- **traefik** namespace is created
- **monitoring** namespace is created

The `kubepi` CLI provides a `preflight` command which checks if everything is in order and every dependency is installed correctly:

```bash
kubepi preflight
```

If `preflight` returned that everything is in order, proceed with the next steps.

First, run the following command which initializes the platform by pulling every submodule required in the `./platform` directory and synchronizes the repositories and its branches. More on using the submodules will be explained later.

```bash
kubepi platform init
```

If the platform is successfully initialized, proceed with creating the cluster:

```bash
kubepi k3d create
```

If everything ran without any errors, the cluster is ready. To check the status of the master node:

```bash
kubectl get nodes -o wide
```

To list the available pods:

```bash
kubectl get pods --all-namespaces -w
```

### Managing `k3d`

k3d is running Kubernetes as Docker containers on your Docker daemon. These Docker containers are stopped when you restart Docker or your RaspberryPI.

Make sure that `k3d` is running:

```bash
kubepi k3d status
```

If `k3d` is up and running you can move to the next section. If it's not running, you can start it with:

```bash
kubepi k3d start
```

If you'd like to stop k3d you can run:

```bash
kubepi k3d stop
```

### Creating Secrets

To be able to use the platform correctly and securely, you need to create the secret resources manually for the services that need them. The secrets are used for authorization on the different services and the use cases will be explained in this section.

#### **Namesilo API Key Secret**

You need to create a secret containing the Namesilo API key. This is required for the LetsEncrypt and DDNS Update configurations to work. You can obtain the Namesilo API key by following these steps:

- Log into your [Namesilo](https://www.namesilo.com/) account
- Go in the [API Manager](https://www.namesilo.com/account/api-manager) section
- Generate a new API Key in the `API Key` section of the page
- Save the key somewhere safe

To create the secret, run the following command and replace the <API_KEY> with your own Namesilo API Key:

```bash
kubectl -n traefik create secret generic namesilo \
        --from-literal='NAMESILO_API_KEY=<API_KEY>'
```

#### **Grafana Admin Password Secret**

You need to set a default password to be able to log into the Grafana Dashboard. You can choose any password you'd like and create the secret with it:

```bash
kubectl -n monitoring create secret generic grafana \
        --from-literal='GF_SECURITY_ADMIN_PASSWORD=<YOUR_PASSWORD>'
```

#### **GitHub Oauth2 Secret**

Before creating the secret, you have to create an application on your GitHub account. You only need to register an "OAuth Application" (as opposed to a full "Github Application"), which you can do [here](https://github.com/settings/applications/new). The fields should be populated like this:

- Application name: `k1s`
- Homepage URL: `https://example.com`
- Application description: `Lorem ipsum description.`
- Authorization callback URL: `https://oauth.example.com/_oauth`

Replace `example.com` with your domain both in the homepage URL and the authorization callback URL.

After creating the application, GitHub will create a `Client ID` and `Client Secret` for the application. Save them somewhere safe, you will need them for creating the secret.

After this, you just need to create a random string which will be used to to sign cookies authentication. To do this, run the following, and save the output somewhere safe:

```bash
openssl rand -hex 16
```

After everything is ready, you can create the secret:

```bash
kubectl -n traefik create secret generic traefik-forward-auth \
        --from-literal='PROVIDERS_GENERIC_OAUTH_CLIENT_ID=<APP_CLIENT_ID>' \
        --from-literal='PROVIDERS_GENERIC_OAUTH_CLIENT_SECRET=<APP_CLIENT_SECRET>' \
        --from-literal='SECRET=<RANDOM_STRING>'
```

## Final Configuration

Before finally running the platform, you need to configure the correct values in several files.

### K1S Dashboard

k1s comes with a preloaded dashboard which is in fact, a submodule located in the `./platform` directory, as the other submodules. You just need to set your domain in its configuration.

- In `./platform/k1s-ui/config.toml`, replace the following with your own domain:

  ```toml
  baseURL = "https://<YOUR_DOMAIN>/"
  ```

- In `./platform/k1s-ui/data/links.yml`, replace the following with your own domain:

  ```yaml
  # Traefik
  url: "https://traefik.<YOUR_DOMAIN>"
  # Grafana
  url: "https://grafana.<YOUR_DOMAIN>"
  # Kubernetes
  url: "https://kube.<YOUR_DOMAIN>"
  # Prometheus
  url: "https://prometheus.<YOUR_DOMAIN>"
  ```

### Required Helm Values

Since k1s is using Helm, the configuration is done in a values YAML file. It is not recommended changing any values which are not mentioned in this section, but if you do, do it on your own risk.

The keys which need configuration are marked with a `# CONFIGURE ME` comment. To configure the values, open `./infrastructure/helm-values.yaml` and set the following values, and make sure you copy/paste them as written in the Value column:

#### **K1S UI**

| Key             | Value                | Description                  |
|-----------------|----------------------|------------------------------|
| ui.ingress.rule | Host(\`<YOUR_DOMAIN>`) | The ingress rule for the UI. |

#### **Traefik**

| Key                        | Value                                          | Description                                                       |
|----------------------------|------------------------------------------------|-------------------------------------------------------------------|
| traefik.args.le.email      | <YOUR_NAMESILO_EMAIL_ADDRESS>                  | The email address you've used to register a domain on Namesilo.   |
| traefik.args.le.caServer   | https://acme-v02.api.letsencrypt.org/directory | LetsEncrypt production server for generating an SSL certificate.  |
| traefik.args.le.mainDomain | "*.<YOUR_DOMAIN>"                              | Your Namesilo domain for which a wildcard certificate is created. |
| traefik.args.le.sanDomain  | "<YOUR_DOMAIN>"                                | The same domain as the main domain.                               |
| traefik.ingress.rule       | Host(\`traefik.<YOUR_DOMAIN>`)                  | The ingress rule for the Traefik dashboard.                       |

> **_NOTE:_** The LetsEncrypt production server can only generate a certificate 5 times per week. The configuration for `traefik.args.le.caServer` above is for the production server, but if you need to test something while developing a new service, use the staging server which allows for infinite certificates: `https://acme-staging-v02.api.letsencrypt.org/directory`.

#### **GitHub Oauth2**

| Key                            | Value                        | Description                                                             |
|--------------------------------|------------------------------|-------------------------------------------------------------------------|
| oauth.env.whitelist.value      | <YOUR_GITHUB_EMAIL_ADDRESS>  | The email address on your GitHub account.                               |
| oauth.env.logoutRedirect.value | https://<YOUR_DOMAIN>        | Redirection URL upon logout. Set your main domain.                      |
| oauth.env.cookieDomain.value   | <YOUR_DOMAIN>                | The domain on which the auth cookie is saved. Must be your main domain. |
| oauth.env.authHost.value       | oauth.<YOUR_DOMAIN>          | The Oauth subdomain which you created in the DNS records.               |
| oauth.ingress.rule             | Host(\`oauth.<YOUR_DOMAIN>`) | The ingress rule for the Oauth2.                                        |

> **_IMPORTANT:_** The whitelist email means that only you can access your own platform. However, as per GitHub's documentation, their `/user` endpoint only returns the user's email if it's publicly visible. As such, you MUST set your email to be public on GitHub.

#### **Prometheus**

| Key                     | Value                             | Description                                    |
|-------------------------|-----------------------------------|------------------------------------------------|
| prometheus.ingress.rule | Host(\`prometheus.<YOUR_DOMAIN>`) | The ingress rule for the Prometheus dashboard. |

#### **Grafana**

| Key                    | Value                          | Description                                   |
|------------------------|--------------------------------|-----------------------------------------------|
| grafana.env.user.value | <ANY_USERNAME_YOU_WANT>        | The admin username for the Grafana dashboard. |
| grafana.ingress.rule   | Host(\`grafana.<YOUR_DOMAIN>`) | The ingress rule for the Grafana dashboard.   |

#### **Kubernetes Dashboard**

| Key                    | Value                      | Description                                    |
|------------------------|----------------------------|------------------------------------------------|
| dashboard.ingress.rule | Host(\`kube.<YOUR_DOMAIN>`) | The ingress rule for the Kubernetes dashboard. |

## Running the Platform

Skaffold is a command line tool that facilitates continuous development for Kubernetes applications. You can iterate on your application source code locally then deploy to local or remote Kubernetes clusters. Skaffold handles the workflow for building, pushing and deploying your application. It also provides building blocks and describe customizations for a CI/CD pipeline.

For more information about how Skaffold works, check the [official documentation](https://skaffold.dev/docs/).

### Skaffold

To start the `k1s` workflow, use the `skaffold` CLI.

There are several ways that you can start the workflow. The following command is the **recommended** one, because the `--cleanup=false` flag allows every Kubernetes resource to stay persistent and not get deleted upon stopping the `skaffold` process:

```bash
skaffold dev --port-forward --force=false --cleanup=false
```

You can also start the workflow with the `--cleanup=true` flag, which is **not recommended** except when adding a new service to the platform and you don't care about persistance in the cluster:

```bash
skaffold dev --port-forward --force=false --cleanup=true
```

If you don't want the service logs to appear, just add the `--tail=false` flag to the command.

> **_WARNING:_** Since Skaffold uses the `kubectl logs -f` command to follow logs from the services, if a service does not get logs in a time interval of 5-10 minutes, a timeout will happen and no logs will be shown for that particular service. This is a Skaffold bug and it's waiting for a fix.

The first time you're running Skaffold on your RaspberryPI might take around 5 minutes, depending on your RaspberryPI version. This is because it is building the submodules and it's pulling the required Docker images for each service.

Once everything is done and Skaffold is up, you can check the status of the pods:

```bash
kubectl get pods --all-namespaces -w
```

Skaffold allows you to make changes to the existing services, or add new ones, without restarting the cluster. This means that it is watching for file changes and automatically rebuilds the services if a change is saved in any service.

### Authentication

Your domain is protected with the Oauth2 setup provided by GitHub. And since you've set a whitelist in the configuration, only you can access your own home cluster.

Once you've logged in, the browser saves an authentication cookie which allows you to use the platform without relogging each time.

If you want to add other users, create another whitelist environment variable with the same name `WHITELIST` in the `k1s-oauth` deployment and set the other user's email in the helm charts by following the same principles.

For more information about environment variables, check [thomseddon's](https://github.com/thomseddon) guide about additional [configuration](https://github.com/thomseddon/traefik-forward-auth#configuration).

### LetsEncrypt SSL Certificate

If you chose the production server in the configuration, you should have a free SSL certificate set up on your domain and on the subdomains, because of the wildcard certificate.

Since the DNS propagation is really slow on Namesilo, it might take up to 40 minutes for a certificate to be generated, so just let it create itself without worrying that it's not working. You can still use everything on the platform while a certificate is being generated.

### Accessing the Dashboards

k1s provides you with several dashboards which you can access via your domain and subdomains. This section explains how to access them.

#### **K1S Dashboard**

Just visit your main domain. For example: `https://example.com`.

#### **Traefik Dashboard**

Open it via the k1s dashboard or visit the subdomain you've created. For example: `https://traefik.example.com`.

#### **Grafana Dashboard**

Open it via the k1s dashboard or visit the subdomain you've created. For example: `https://grafana.example.com`.

To log into the dashboard, use the username and password you've created in the secrets and the helm values configuration.

#### **Prometheus Dashboard**

Open it via the k1s dashboard or visit the subdomain you've created. For example: `https://prometheus.example.com`.

#### **Kube Dashboard**

Open it via the k1s dashboard or visit the subdomain you've created. For example: `https://kube.example.com`.

To get into the dashboard, you will need the platform token. You can get the token by using the relevant `kubepi` command:

```bash
kubepi platform token
```

> **_NOTE:_** For some reason, if you close the tab and try to access the Kubernetes dashboard, you might get an error. To fix this, just log out from the dashboard and use the same token to log in.

### Pulling Changes

When pulling changes with `git pull` and you're using submodules, you must run the following command to pull the submodule changes and synchronize the platform again:

```bash
kubepi platform init
```

### Getting the Platform URL

To get the main URL of the platform, which is the K1S Dashboard, you can run:

```bash
kubepi platform info
```

### Checking Submodule Versions

To get the current submodule branches and commit hashes, run:

```bash
kubepi platform version
```

### Checking the Logs Manually

If you want to check the logs of a particular service, you can do the following in a separate terminal window:

- Check the names and the namespaces of the running pods:

  ```bash
  kubectl get pods --all-namespaces
  ```

- Get the logs:

  ```bash
  kubectl logs -f -n <NAMESPACE> <POD_NAME>
  ```

## Adding New Services

The platform is made with extensibility in mind, so that you can add your own services without too much hassle. This section explains how to do it.

> **_NOTE:_** You will probably need some knowledge about creating Kubernetes manifests and using Helm before adding a new service.

There are two ways to do this, by using submodules or simply doing it locally. The submodules way is **recommended** because it allows you to use version control and swap between version whenever you want by using the `git` CLI.

### The Submodules Way

Make sure you're in the root directory of the platform. Then add a new submodule from an existing repository. For example:

```bash
git submodule add git@github.com:nushkovg/k1s-example.git platform/k1s-example
```

This will create a new directory called `k1s-example` in the `./platform` directory. After doing this, run `kubepi platform init` to get the latest changes and synchronize the platform.

### The Local Way

To begin, create a new directory in the `./platform` directory. For example, create a `./platform/k1s-example` directory. In there, you can create any kind of service.

### Infrastructure Configuration

After using either the submodules or the local way of adding a service, you need to create the infrastructure manifests and initialize a new Helm Chart.

As the first step, create a new directory in `./infrastructure` with the same name as the directory for the service, for example `./infrastructure/k1s-example`.

#### **Creating the Chart**

In the `./infrastructure/k1s-example` directory, create a `Chart.yaml` file with the following contents:

```yaml
name: k1s-example
version: 0.0.1
platform: k1s
description: K1S Example Helm Chart

```

After that, add a `.helmignore` file. You can just copy it from any other service in the `./infrastructure/k1s-example` directory.

#### **Adding the Kubernetes Manifests**

In the `./infrastructure/k1s-example`, create another directory called `templates`. In here you can add any kind of a Kubernetes resource that your service requires. It is recommended that you follow the naming convention of the other services for the manifests.

After doing this, you should transform the manifests into Helm templates. To do this, you must add the new service and its values in `./infrastructure/helm-values.yaml`.

For example, add a new section like this at the bottom of the file:

```yaml
###############################
## K1S Example Configuration ##
###############################

example:
  name: example
  namespace: k1s
  replicas: 1

  ports:
    port: 443
    targetPort: 8443
    protocol: TCP
  
  image: # set automatically in skaffold
```

Whatever you do, **DO NOT** add the image name manually. Skaffold does this for you since it's building it itself.

After adding the values, replace the relevant fields in the manifests. Use the other services as a reference on how to do this if you're new to Helm.

### Editing the Skaffold Configuration

Once you've done everything, you are ready to add the new service to the `./skaffold.yaml` configuration.

#### **Adding the ARM build script**

First, make sure to add the following bash script in the `./platform/k1s-example/scripts` directory, and name it `build.sh`:

```bash
#!/bin/bash

# Enable buildx features for cross-architecture builds
export DOCKER_CLI_EXPERIMENTAL=enabled

# Build the image
docker buildx build --platform linux/arm/v7 --tag $IMAGE .
```

After this, give the necessary permissions to the script:

```bash
chmod +x ./platform/k1s-example/scripts/build.sh
```

You will need this script because Skaffold needs to know how to build your service for an ARM architecture, which the RaspberryPI uses.

#### **Adding the service**

In `skaffold.yaml`, add the following sections:

- Under `build.artifacts`:
  
  ```yaml
  - context: platform/k1s-example
    image: k1s-example
  ```

- Under `profiles.build.artifacts`:

  ```yaml
  - context: platform/k1s-example
    image: k1s-example
    custom:
      buildCommand: ./scripts/build.sh
    sync: {}
  ```

- Under `profiles.deploy.helm`:

  ```yaml
  - name: k1s-example
    namespace: k1s
    chartPath: infrastructure/k1s-example
    valuesFiles:
    - infrastructure/helm-values.yaml
    artifactOverrides:
      example.image: k1s-example
  ```

#### **Adding a DNS Record**

In case your service has a UI, you can create a new DNS record for the subdomain as a CNAME, just like the other subdomains.

#### **Adding the Service to K1S Dashboard**

If you'd like to add your own service to the k1s dashboard, you need to edit the `./platform/k1s-ui/data/links.yml` file and optionally add a logo. Here are the steps:

- In `./platform/k1s-ui/data/links.yml`, add the following at the bottom:

  ```yaml
  -
  name: "Example Service"
  url: "https://example-service.example.com"
  img: "logos/example-service.svg" # This is optional
  tags: ["monitoring"]
  ```

- Optionally, add a logo (preferably in a SVG format) in `./platform/k1s-ui/static/logos`.

#### **Testing the Service**

After this, just restart the Skaffold process and test the functionality of the service. If something is wrond, check if you've missed a step. If you think there is something wrong with the platform itself, please open an issue in this repository.

## Known Issues

- Prometheus can't scrape the metrics sometimes because the brower time and the local time are different on Linux. To fix this, use the following command:

  ```bash
  timedatectl set-local-rtc 1 --adjust-system-clock
  ```

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
