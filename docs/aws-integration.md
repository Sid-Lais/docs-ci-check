# Connect Your AWS Account

Connecting your AWS account is the first step toward enabling full cost visibility in Amnic. This integration allows Amnic to ingest billing data, usage metrics, and Kubernetes cost splits using a **secure, read-only cross-account role**.

Amnic does **not** modify any of your cloud resources. It only reads the data necessary for analytics, optimization, and anomaly detection.

### **What You’ll Learn**

This guide covers how to connect your AWS account to Amnic, the required permissions, using an existing or new CUR, and what happens after setup.

## **What This Integration Enables**

Once your AWS account is successfully connected, Amnic will begin retrieving important cloud data, such as:

* **Cost and Usage Reports (CUR)** from Amazon S3 to provide deep cost insights and forecasting capabilities
* **Account metadata and CUR configurations** for comprehensive cost breakdown and visibility
* **Kubernetes (EKS) cost allocation data** (if enabled) to allow granular cost visibility for workloads running on Amazon EKS

This data fuels Amnic’s key features, including the **Cost Analyzer**, **Budgets**, **Anomalies**, **Dashboards**, and **Kubernetes cost optimization insights**.

## **Required Permissions**

Amnic requires specific permissions to access the necessary data for secure cost analysis. These permissions are granted through a **read-only IAM role** provisioned via a CloudFormation stack. The required permissions are as follows:

* `s3:Get*`: Allows Amnic to fetch **Cost and Usage Reports (CUR)** stored in your S3 bucket.
* `cur:DescribeReportDefinitions`: Enables Amnic to understand your CUR report's structure.
* `organizations:ListAccounts`: Required to retrieve metadata about linked accounts in your AWS organization.
* `cloudwatch:GetMetricData, cloudwatch:ListMetrics`, and similar permissions are required if CloudWatch-based cost allocation or anomaly detection is enabled
* **K8s split cost allocation** data enabled. Refer to the [AWS documentation](https://docs.aws.amazon.com/cur/latest/userguide/enabling-split-cost-allocation-data.html).

**Note**: Amnic will never modify any of your AWS resources; it only uses read-only permissions to extract necessary data for cost insights.

## **Step-by-Step Setup**

### **Choose a Setup Path**

You can either create a new CUR or connect an existing one.

![Connect You AWS Account](/images/AMNIC_INTEGRATIONS_CONNECT_AWS.png)

Vantage
Cloudzero

## **Option 1: Create a New CUR**

If you haven't configured a **Cost and Usage Report (CUR)** yet, you can create a new one through Amnic’s AWS integration wizard.

### **1\. Open the AWS Integration Wizard**

In Amnic:

![Connect You AWS Account 2](/images/AMNIC_INTEGRATIONS_CONNECT_AWS-2.png)

![Connect You AWS Account 2](/images/AMNIC_INTEGRATIONS_CONNECT_AWS_2.png)

* Go to **Settings → Integrations**
* Click **AWS** to open the connection wizard
* Choose whether to create a new Cost and Usage Report (CUR) or use an existing one

If using an existing CUR, refer to the [existing CUR flow](#option-2:-use-an-existing-cur).

### **2\. Deploy the CloudFormation Template**

* Click **Launch Template** to open CloudFormation in your AWS billing/master account
* The CloudFormation stack creates a secure IAM role in your AWS billing account

In the AWS console:

* Review the IAM permissions and external ID
* Acknowledge the changes
* Click **Create Stack** and monitor progress

### **3\. Retrieve the Role ARN**

Once the stack is created:

* You will see the **resource ARN**, **external ID**, and **S3 bucket** name/path. (Amnic automatically creates a new CUR report in your S3 bucket.)
* Navigate to the **Outputs** tab
* Copy the `CrossAccountRoleArn` value

### **4\. Return to Amnic and Complete the Setup**

* Paste the Role ARN into the setup form in Amnic
* Click **Next** to validate the connection

Amnic will confirm permissions and begin ingestion.

## **Option 2: Use an Existing CUR** {#option-2:-use-an-existing-cur}

If you already have a configured **Cost and Usage Report (CUR)** in your AWS account and would like to allow Amnic access to it, follow the steps below to manually create a secure IAM role and policy.

This option is ideal when you do not want to use Amnic’s automated CloudFormation template and instead prefer to connect your existing billing pipeline manually.

### **1\. Create a Cross-Account IAM Role**

1. Sign in to your **AWS Console** with admin permissions.
2. Navigate to: **IAM → Roles → Create role**

3. Choose **Custom Trust Policy** and paste the following into the trust relationship box:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::924148612171:root"
        ]
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "<amnic-to-provide-this-id>"
        }
      }
    }
  ]
}
```

4. Replace `<amnic-to-provide-this-id>` with the **External ID** shared by your Amnic contact.

5\. Click **Next**, assign a role name (e.g., `amnic-assume-cost-role`) and proceed to create the role.

### **2\. Attach Inline Policy for CUR, S3, and Metrics Access**

Once the role is created:

1. Go to the role's **Permissions** tab.
2. Click on **Add Permissions** and **Create inline policy**.

3. Switch to **JSON** and paste the following IAM policy, and update the `<Bucket_Name>` placeholders with the name of the S3 bucket where your CUR reports are stored:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "organizations:Describe*",
        "cur:DescribeReportDefinitions",
        "ce:GetReservationPurchaseRecommendation",
        "bcm-data-exports:ListExports",
        "bcm-data-exports:GetExport"
      ],
      "Resource": ["*"],
      "Effect": "Allow",
      "Sid": "CURAccess"
    },
    {
      "Action": [
        "tag:GetResources",
        "cloudwatch:GetMetricData",
        "cloudwatch:GetMetricStatistics",
        "cloudwatch:ListMetrics",
        "ec2:DescribeTags",
        "ec2:DescribeInstances",
        "ec2:DescribeRegions",
        "ce:GetReservationPurchaseRecommendation"
      ],
      "Resource": ["*"],
      "Effect": "Allow",
      "Sid": "CWRecommendations"
    },
    {
      "Action": [
        "s3:Get*",
        "s3:List*"
      ],
      "Resource": [
        "arn:aws:s3:::<Bucket_Name>",
        "arn:aws:s3:::<Bucket_Name>/*"
      ],
      "Effect": "Allow",
      "Sid": "S3Access"
    }
  ]
}
```

4. Click **Review policy**, give it a name (e.g., `AmnicCURAccessPolicy`), and save it.

### **3\. Share Integration Details with Amnic**

After the role and policy are created, provide the following details to your Amnic contact:

* **Role ARN** of the newly created IAM role
* **S3 Path with Prefix**: The exact S3 path where your CUR files are delivered (e.g., `s3://my-billing-bucket/amnic-reports/`)

Amnic will use this information to begin ingesting your CUR data securely.

## **What Happens Next**

After submitting the Role ARN, Amnic will validate access and begin ingesting your cost and usage data. This may take up to 12 hours, depending on AWS report delivery schedules.

Once the data is available:

* **Explore your data**: You’ll be able to view detailed spend breakdowns and cost insights in the **Cost Analyzer**.
* **Set up budgets and alerts**: Begin configuring budgets and establishing alerts to track your cloud spending.
* **Review anomalies**: Amnic will begin analyzing the data for any cost anomalies, helping you stay on top of unexpected expenses.

If you don’t see your data after 12 hours, please ensure your CUR is properly configured or reach out to [support@amnic.com](mailto:support@amnic.com) for assistance. For help with common setup issues, refer to the [Troubleshooting AWS Integration page](?tab=t.6hbvb2em5yia).

## **Disconnect AWS Integration**

[IMAGE_PLACEHOLDER]

If you no longer wish to use Amnic with your AWS account, you can disconnect the integration at any time. This action removes Amnic’s access and ensures that no further data is ingested.

### **How to Disconnect**

1. **Delete the CloudFormation Stack**

   1. Go to the **AWS CloudFormation Console**.
   2. Locate the stack that was created during the Amnic integration setup (usually named something like `amnic-cost-access`).
   3. Select the stack and click **Delete**.
   4. Confirm the deletion when prompted.

2. **Verify IAM Role and Policies are Removed**

   1. The CloudFormation stack will delete:

      * The IAM role (`amnic-assume-cost-role`)
      * Any managed policies created for CUR or CloudWatch access
      * The S3 bucket (if it was created as part of the stack) used for Cost and Usage Reports, unless it contains retained data

   2. Navigate to the **IAM console** and verify that the role and policies are no longer present under "Roles" and "Policies".

3. **Validate S3 and CUR Cleanup (If Applicable)**

   1. If Amnic created a new S3 bucket and CUR, the deletion process will remove the bucket *unless* it has **retained objects**. In such cases:

      * Manually delete any objects inside the bucket before retrying deletion
      * Alternatively, retain the S3 bucket and CUR report if you wish to reuse it later

### **Note**

* Disconnecting the integration will stop any further data ingestion.
* Historical cost data already ingested into Amnic will remain unless manually purged (contact [support@amnic.com](mailto:support@amnic.com) to do so).
* If you re-enable the integration later, a new CloudFormation stack will need to be deployed.
