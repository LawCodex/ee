---
title: "Requirements for the electronic submission of reports"
identifier: "525062018001"
rt_reference: "RT V, 25.06.2018, 1"
group_id: "100707"
type: regulation
issuer: "Eesti Panga President"
number: "4"
text_type: "algtekst-terviktekst"
jurisdiction: ee
language: en
date: 2018-05-29
last_amended: 2019-01-01
status: in_force
source: "https://www.riigiteataja.ee/en/akt/525062018001"
retrieved: 2026-10-11
translation: unofficial
translation_of: "105062018001"
---

# Requirements for the electronic submission of reports

> Unofficial English translation published by Riigi Teataja. Only the Estonian text is legally binding.

This decree is established on the basis of subsection 91 (1) of the Credit Institutions Act.

## Chapter 1 — General Provisions

### § 1. Scope of the decree

This decree establishes the technical requirements for the electronic submission of reports to Eesti Pank and the Financial Supervision Authority.

### § 2. Application of the decree

This decree applies to the credit institutions and foreign branches operating in Estonia who are required to submit reports to Eesti Pank and the Financial Supervision Authority.

### § 3. Definitions

For the purposes of this decree, the following definitions are used:

1\) **report** is a set of accurate data, created and rendered in compliance with the relevant regulation;

2\) **reporting entity** is the legal person obliged to submit reports;

3\) **recipient of report** is Eesti Pank or the Financial Supervision Authority;

4\) **report message** is a valid document containing the report, either in XML (Extensible Markup Language, as defined in the relevant recommendation of the World Wide Web Consortium, https://www.w3.org/TR/xml/) or XBRL (eXtensible Business Reporting Language) format;

5\) **data collection portal** is a software application managed jointly by Eesti Pank and the Financial Supervision Authority for receiving and processing electronic reports, which can be accessed at https://aruandlus.eestipank.ee;

6\) **transmission of report** is making the report message electronically available to the recipient of report (either by e-mail, web service, uploading the file in the data collection portal, manually entering data or importing from a file);

7\) **submission of report** is the transmission of a valid, compliant and accurate report to the recipient of report in accordance with the relevant regulation.

## Chapter 2 — Submission of reports, format of report messages and security requirements

### § 4. Submission of reports

(1) Reports are submitted to the recipient of report in the data collection portal.

(2) The following options may be used for submitting reports:

1\) by manually entering the data in the report in the data collection portal;

2\) by importing the data from a file into the report in the data collection portal;

3\) by uploading the report file in the data collection portal;

4\) by e-mailing the report to the data collection portal;

5\) by rendering the report to the data collection portal, using a web service.

(3) If the e-mailing or web service option is used, the report message must be secured. Secure attachments are transmitted to the addresses provided under Statistics > For Reporters in Eesti Pank’s website. Each attachment may contain one or several report messages.

(4) In case a web service is used, the data transmission protocol shall be defined by schemas and documents provided under Statistics > For Reporters in Eesti Pank’s website.

### § 5. Format of reports

(1) In case the report is submitted by e-mail or web service or the report file is uploaded in the data collection portal, the report message must be formatted as either an XML- or XBRL-document, as prescribed by the relevant regulation.

(2) The structure and content of report messages formatted as XML documents are based on XML schemas (http://www.w3.org/standards/xml/Schema) referred to at https://aruandlus.eestipank.ee/reports/.

(3) Reports submitted in the XBRL format must comply with the requirements established by the relevant regulation and published on the European Banking Authority (EBA) website (https://www.eba.europa.eu/risk-analysis-and-data/reporting-frameworks).

(4) The XML schema of a report is the formalised presentation of the content of the report as prescribed by law. Report messages are formally validated against the XML schema.

(5) The codes for XML reports, specifications for formatting report messages and examples thereof are provided under Statistics > For Reporters in Eesti Pank’s website.

### § 6. Securing report messages

(1) If a public channel is used for the transmission of a report message (e.g. e-mail), the report message must be encrypted and digitally signed.

(2) If a secure channel is used for the transmission of a report message (e.g. HTTPS), the report message may be only digitally signed.

(3) The following security options are considered acceptable:

1\) Open PGP;

2\) DigiDoc;

3\) x.509 certificate.

(4) The reporting entity is responsible for the management of the keys and certificates required for data transmission. The keys and certificates are managed in the data collection portal.

(5) The specifications for the security options referred to in subsection 3 of this section are provided under Statistics > For Reporters in Eesti Pank’s website.

### § 7. User management

(1) The reporting entity is responsible for user management (authorisation, rights assignment, updating contact data, terminating powers of attorney etc).

(2) The data collection portal is used for user management.

### § 8. Primary processing of report messages

(1) Primary processing of report messages takes place in the data collection portal.

(2) The data collection portal shall send the reporting entity a confirmation concerning the receipt of a report message only if the reporting entity has requested such confirmation. This message also serves as a confirmation for the reporting entity by the recipient of report that the report message has been received in the data collection portal.

(3) Messages concerning errors found in report messages are sent to the recipient named by the reporting entity. In case a public data transfer channel is used, error reports shall be transmitted to the reported entity in an encrypted form.

(4) Error reports regarding the contents of the report are sent by e-mail or web service to the person filing the report and these users of the reporting entity who have requested error reports in the data collection portal.

### § 9. Transmission of warnings to reporting entities

If a valid report has not been submitted by the due date, a warning is sent to the e-mail addresses designated by the authorised representatives of the reporting entity.

### § 10. Effective submission

A report is deemed to have been submitted if its content is correct and the report has been prepared and rendered in compliance with the requirements established by this decree.

## Chapter 3 — Implementing provisions

### § 11. Revocation of a decree

Eesti Pank Governor’s decree No 9 of 9 December 2011 ‘Requirements for submission of reports formatted as XML documents’ (RT I, 14.12.2011, 12) is repealed.

### § 12. Entry into force

This decree enters into force on 1 January 2019.

---

Ardo Hansson, Governor
