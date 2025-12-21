# publish-mavencentral

## Usage

### Apply script
At the bottom of the `build.gradle` file in each module
```groovy
apply from: "https://raw.githubusercontent.com/PaystackHQ/publish-mavencentral/main/maven-publish.gradle"
```

### Define library details
In project-level `gradle.properties` file
```properties
# Replace these with the relevant values

GROUP=co.paystack.android.whatever
VERSION_NAME=1.0.0

POM_DESCRIPTION=Library description

POM_URL=https://github.com/PaystackHQ/library-uri
POM_SCM_URL=https://github.com/PaystackHQ/library-uri
POM_SCM_CONNECTION=scm:git:github.com/PaystackHQ/library-uri.git
POM_SCM_DEV_CONNECTION=scm:git:ssh://github.com/PaystackHQ/library-uri.git

POM_LICENCE_NAME=The Apache Software License, Version 2.0
POM_LICENCE_URL=http://www.apache.org/licenses/LICENSE-2.0.txt
POM_LICENCE_DIST=repo

POM_DEVELOPER_ID=paystack
POM_DEVELOPER_NAME=Paystack
POM_DEVELOPER_EMAIL=developers@paystack.co
```
In each library module's `gradle.properties` file (create one if it doesn't exist)
```properties
# Replace these with the relevant values

POM_ARTIFACT_ID=artifactid
POM_NAME=Library name
POM_PACKAGING=aar
```

### Define secrets
This step is only important when submitting artifacts to the maven central repository.
These values will be read from system environment variables if `local.properties` doesn't exist. Useful in CI environments.

#### Artifact signing credentials
In `local.properties` file
```properties
signing.keyId=insert_signing_key_id
signing.password=insert_signing_key_password_here
signing.secretKeyRingFile=/path/to/secretkey/file,gpg
```
#### Sonatype OSSRH credentials
In `local.properties` file
```properties
ossrhUsername=insert_ossrh_username
ossrhPassword=insert_ossrh_password
```
