import glob
import os 
import re
import shutil
import sys
import tempfile

from contextlib import contextmanager
from string import Template

#fabric imports
from fabric.api import *

#Import project version
import version

env.project = os.path.basename(os.path.dirname(__file__))
env.project_dir = os.path.dirname(__file__)
env.project_version =  version.VERSION
env.project_user = "tr"
env.project_group = "tr"



def localdev():
    """Configure environment for localdev """

    env.hosts = ["localdev"]
    env.project_environment="localdev"
    env.project_install_root="/opt/tr/services/%s/install" % (env.project)
    env.project_deploy_root="/opt/tr/services/%s/%s" % (env.project, env.project_environment)

    #Add additional convenience root for localdev deploy
    env.project_localdev_deploy_root="/opt/tr/services/localdev.com/%s" % env.project_environment

def integration():
    """Configure environment for integration """

    env.hosts = ["dev.techresidents.com"]
    env.project_environment="integration"
    env.project_install_root="/opt/tr/services/%s/install" % (env.project)
    env.project_deploy_root="/opt/tr/services/%s/%s" % (env.project, env.project_environment)

def staging():
    """Configure environment for staging """

    env.hosts = ["dev.techresidents.com"]
    env.project_environment="staging"
    env.project_install_root="/opt/tr/services/%s/install" % (env.project)
    env.project_deploy_root="/opt/tr/services/%s/%s" % (env.project, env.project_environment)

def prod():
    """Configure environment for staging """

    env.hosts = ["dev.techresidents.com"]
    env.project_environment="prod"
    env.project_install_root="/opt/tr/services/%s/install" % (env.project)
    env.project_deploy_root="/opt/tr/services/%s/%s" % (env.project, env.project_environment)




@contextmanager
def _tempdir():
    """Context Manager for temp directories"""
    try:
        tempdir_name = tempfile.mkdtemp()
        yield tempdir_name
    finally:
        shutil.rmtree(tempdir_name)

def _create_app_tarball(tag="HEAD", release="1", arch="x86_64"):
    """Helper to create application tarball"""

    tarball = "%s-%s.tar.gz" % (env.project, env.project_version)

    if tag.lower() == "working":
        with _tempdir() as tempdir_name:
            versioned_project = "%s-%s" % (env.project, env.project_version)
            local("mkdir %s" % os.path.join(tempdir_name, versioned_project))
            local("ln -s %s %s" % (env.project_dir, os.path.join(tempdir_name, versioned_project, env.project)))
            local("tar -C %s -cLzf %s %s" % (tempdir_name, tarball, versioned_project))

    else:
        #git archive --format=tar --prefix=techresidents_web-0.1/techresidents_web/ HEAD |gzip > techresidents__web-0.1.tar.gz
        local("git archive --format=tar --prefix={0}-{1}/{0}/ {2} |gzip > {3}".format(env.project, env.project_version, tag, tarball))

        #Check that the version in the local version.py matches the archive
        with _tempdir() as tempdir_name:
            #Unpackage the git archive in tempdir and add it to syspath
            local("tar -C %s -xf %s" % (tempdir_name, tarball))
            sys.path.append(os.path.abspath(os.path.join(tempdir_name, "%s-%s" % (env.project, env.project_version))))
            
            tempmodule = "%s.version" % env.project
            __import__(tempmodule)

            #If the versions do not match, fix the tarball
            if sys.modules[tempmodule].VERSION != version.VERSION:
                local("rm %s" % tarball)
                env.project_version = sys.modules[tempmodule].VERSION
                tarball = "%s-%s.tar.gz" % (env.project, env.project_version)
                local("git archive --format=tar --prefix={0}-{1}/{0}/ {2} |gzip > {3}".format(env.project, env.project_version, tag, tarball))
    
    return tarball

def _file_replace(fileglob, pattern, replacement, count=0, flags=re.DOTALL, expected_substitutions=1):
    """Helper to replace a pattern in a file."""
    for filename in glob.glob(fileglob):
        with open(filename, 'r') as f:
            data = f.read()
        
        result, substitutions = re.subn(pattern, replacement, data, count, flags)
        if substitutions != expected_substitutions:
            raise RuntimeError("number of substitutions (%d) != expected substitutions (%d)"\
                    % (substitutions, expected_substitutions))

        with open(filename, 'w') as f:
            f.write(result)

def build_rpm(tag="HEAD", release="1", arch="x86_64"):
    """Build and package application for release in an rpm.
       The build is done on exactly remote machine and resulting rpm is copied back.

       Typical invocation: fab localdev build_rpm

         version - rpm version 
         tag     - git tag (treeish) to package or if "working" use working directory
         release - rpm release number (get appended to version, i.e. 1.0-<release>)
         arch    - rpm architecture

       Examples:
          fab localdev build_rpm:tag=HEAD
          fab localdev build_rpm:tag=1.0
    """

    if len(env.hosts) != 1:
        raise RuntimeError("build_rpm must be run on exactly 1 remote machine")

    tarball = _create_app_tarball(tag, release, arch)

    #Setup rpmbuild tree in home directory on remote build box
    run("rpmdev-setuptree")

    #Copy over the tarball and spec file
    put(tarball, os.path.join("rpmbuild", "SOURCES"))
    
    #Create rpm spec file from template and copy over to the remote build box
    with open(os.path.join("deploy", "rpm_template.spec"), "r") as rpm_template:
        specfileName = os.path.join("deploy", "%s-%s.spec" % (env.project, env.project_version))
        with open(specfileName, 'w') as specfile:
            #Create new spec from template
            template_dict = {"template_name": env.project, "template_version": env.project_version, "template_release": release}
            spec_content = Template(rpm_template.read()).safe_substitute(template_dict)

            #Save new specfile
            specfile.write(spec_content)
       
        put(specfileName, os.path.join("rpmbuild", "SPECS"))
    
    #Build rpm
    run("rpmbuild -v -bb %s" % os.path.join("rpmbuild", "SPECS", os.path.basename(specfileName)))

    #Copy rpm to local machine
    get(os.path.join("rpmbuild", "RPMS", "{0}/{1}-{2}-{3}.{0}.rpm".format(arch, env.project, env.project_version, release)), ".")


def install(version, release="1", arch="x86_64"):
    """Install rpm on specified environment.
       Note resulting rpm must exist in current directory.
       
       Typical invocation: fab integration install
    """
    
    #Use project_version if version not explicitly provided
    version = version or env.project_version

    rpm = "{0}-{1}-{2}.{3}.rpm".format(env.project, version, release, arch)
    if not os.path.exists(rpm):
        raise RuntimeError("rpm file, %s,  does not exist. Execute build_rpm to create it." % rpm)

    with settings(user="root"):
        run("mkdir -p %s" % os.path.join(env.project_install_root))
        put(rpm, env.project_install_root)
        run("rpm --oldpackage -ivh %s" % os.path.join(env.project_install_root, rpm))


def list_installed():
    """List installed rpms on specified environments."""
    run("rpm -q %s" % env.project)


def deploy(version):
    """Deploy to specified environments.
       This will update symbolic links so Apache will pick up new application.
       Target app must have already been packaged and installed on target machines.
    """

    target = os.path.join(env.project_install_root, "%s-%s" % (env.project, version), env.project)

    #Verify target version is installed
    run("ls -ldtr %s" % target)
    
    with settings(user="root"):
        run("ln -fns %s %s" % (target, os.path.join(env.project_deploy_root, env.project)))
        
def restart_service():
    """
        Restart service on specified environments.
        This should be necessary for normal deployments.
    """

    with settings(user="root"):
        restart_path = os.path.join(env.project_deploy_root, env.project, "bin", "restart")
        restart_command = "%s %s" % (restart_path, env.project_environment)
        run(restart_command)


def uninstall(version):
    """Uninstall rpm on specified environment.
         version - comma separated list of versions
    """

    with settings(user="root"):
        run("rpm -ev %s-%s" % (env.project, version))


def bump_version(current_version, new_version):
    info = {
        "service": env.project,
        "current_version": current_version,
        "new_version": new_version
    }

    _file_replace(
            fileglob="version.py",
            pattern=r"{current_version}".format(**info),
            replacement=r"{new_version}".format(**info))
    
    _file_replace(
            fileglob="{service}-idl/pom.xml".format(**info),
            pattern=r"<artifactId>{service}-idl</artifactId>(.*)<version>{current_version}</version>".format(**info),
            replacement=r"<artifactId>{service}-idl</artifactId>\1<version>{new_version}</version>".format(**info))

    _file_replace(
            fileglob="{service}-idl/*/pom.xml".format(**info),
            pattern=r"<parent>(.*){current_version}(.*)</parent>".format(**info),
            replacement=r"<parent>\g<1>{new_version}\g<2></parent>".format(**info))

    _file_replace(
            fileglob="requirements/requirements.txt",
            pattern=r"{service}-idl-python/{current_version}/{service}-idl-python-{current_version}-bin.tar.gz".format(**info),
            replacement=r"{service}-idl-python/{new_version}/{service}-idl-python-{new_version}-bin.tar.gz".format(**info))

def release(new_version, new_snapshot_version, current_version=None):
    """Cut release"""

    if len(env.hosts) != 1:
        raise RuntimeError("release must be run on exactly 1 remote machine")

    new_major_version = new_version.rsplit('.', 1)[0]

    info = {
        "service": env.project,
        "current_version": current_version or "%s-SNAPSHOT" % new_major_version,
        "new_version": new_version,
        "new_major_version": new_major_version,
        "new_snapshot_version": new_snapshot_version,
        "release_branch": "release-%s" % new_major_version
    }

    answer = prompt("Releasing with the following parameters\n\n%s\n\nContinue with release?" % info, default="n")
    if answer not in ["Y", "y", "Yes", "YES"]:
        return

    #pull the latest
    local("git checkout master")
    local("git pull")
    local("git checkout integration")
    local("git pull")

    #create and checkout release branch
    local("git checkout integration")
    local("git branch {release_branch}".format(**info))
    local("git push origin {release_branch}".format(**info))
    local("git branch --set-upstream {release_branch} origin/{release_branch}".format(**info))
    local("git checkout {release_branch}".format(**info))

    #bump release branch versions
    bump_version(info["current_version"], info["new_version"])

    #deploy idl to nexus
    with lcd("{service}-idl".format(**info)):
        local("mvn clean deploy")

    #commit changes to release branch and push 
    local("git commit -a -m 'Bumping version to {new_version}'".format(**info))
    local("git push")

    #build rpm
    build_rpm()
    
    #Checkout master and merge release
    local("git checkout master")
    local("git branch --no-merged")
    local("git merge --no-ff {release_branch}".format(**info))
    local("git tag -a {new_version} -m 'Release {new_version}'".format(**info))
    local("git push --all")
    local("git push --tags")
    local("git branch --no-merged")

    #Checkout integration branch and merge release
    local("git checkout integration")
    local("git branch --no-merged")
    local("git merge --no-ff {release_branch}".format(**info))
    local("git branch --no-merged")

    #bump release branch versions
    bump_version(info["new_version"], info["new_snapshot_version"])

    #deploy idl to nexus
    with lcd("{service}-idl".format(**info)):
        local("mvn clean deploy")

    local("git commit -a -m 'Bumping version to {new_snapshot_version}'".format(**info))
    local("git push")
