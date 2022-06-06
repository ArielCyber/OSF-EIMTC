# Datasets
In this directory there is information and links of various datasets.

# Table Of Contents
- [Datasets](#datasets)
  * [VPN-nonVPN (ISCXVPN2016)](#vpn-nonvpn--iscxvpn2016-)
    + [Other Versions](#other-versions)
    + [Some Papers That Adopted This Dataset](#some-papers-that-adopted-this-dataset)
  * [USTC-TFC2016](#ustc-tfc2016)
    + [Some Papers That Adopted This Dataset](#some-papers-that-adopted-this-dataset-1)
  * [Ariel (BOA2016)](#ariel--boa2016-)
    + [Some Papers That Adopted This Dataset](#some-papers-that-adopted-this-dataset-2)
  * [malware-traffic-analysis.net (MTA)](#malware-traffic-analysisnet--mta-)
    + [Some Papers That Adopted This Dataset](#some-papers-that-adopted-this-dataset-3)
  * [StratosphereIPS Labs Datasets (Starto)](#stratosphereips-labs-datasets--starto-)
    + [Some Papers That Adopted This Dataset](#some-papers-that-adopted-this-dataset-4)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>


# Dataset information

## VPN-nonVPN (ISCXVPN2016)

- Link: https://www.unb.ca/cic/datasets/vpn.html
- Description: This dataset consists of 150 PCAP files of different types of traffic and applications. Each PCAP file has an application category (e.g., Spotify, Facebook, YouTube, etc.), a traffic type category (e.g., streaming, VoIP, chat, etc.) and an encapsulation label (non-VPN/VPN). 
- Downloadable Size: ~24.9 GB

### Other Versions

- Cleaned (by paper **2** below)
    - Link: https://msmailarielac-my.sharepoint.com/:f:/g/personal/adi_lichy_msmail_ariel_ac_il/EgijU1zPAcVLraRhYqMte2IB2XPHj850n1XL0kT4KQjbEg?e=e1u9BL
    - Note: The link may expire, contact the authors of paper **2** below for the updated link.
    - Description: Cleaned unrelated traffic such as BlueStacks, DropBox broadcasts, and others. Renamed file names to use a consistant label-based naming scheme.

### Some Papers That Adopted This Dataset 
1. *T. Shapira and Y. Shavitt, "FlowPic: Encrypted Internet Traffic Classification is as Easy as Image Recognition," IEEE INFOCOM 2019 - IEEE Conference on Computer Communications Workshops (INFOCOM WKSHPS), 2019, pp. 680-687, doi: 10.1109/INFCOMW.2019.8845315.*
2. *O. Bader, A. Lichy, C. Hajaj, R. Dubin and A. Dvir, "MalDIST: From Encrypted Traffic Classification to Malware Traffic Detection and Classification," 2022 IEEE 19th Annual Consumer Communications & Networking Conference (CCNC), 2022, pp. 527-533, doi: 10.1109/CCNC49033.2022.9700625.*
3. *Barut, Onur, et al. “NetML: A Challenge for Network Traffic Analytics.” CoRR, vol. abs/2004.13006, 2020, https://arxiv.org/abs/2004.13006.*
4. *Aceto, Giuseppe, et al. “DISTILLER: Encrypted Traffic Classification via Multimodal Multitask Deep Learning.” J. Netw. Comput. Appl., vol. 183–184, 2021, p. 102985, doi:10.1016/j.jnca.2021.102985.*
5. *Barut, Onur, et al. “Multi-Task Hierarchical Learning Based Network Traffic Analytics.” ICC 2021 - IEEE International Conference on Communications, 2021, pp. 1–6, doi:10.1109/ICC42927.2021.9500546.* 
6. *Wang, Wei, et al. “End-to-End Encrypted Traffic Classification with One-Dimensional Convolution Neural Networks.” 2017 IEEE International Conference on Intelligence and Security Informatics, ISI 2017, Beijing, China, July 22-24, 2017, IEEE, 2017, pp. 43–48, doi:10.1109/ISI.2017.8004872.* 
7. *Draper-Gil, Gerard, et al. “Characterization of Encrypted and VPN Traffic Using Time-Related Features.” Proceedings of the 2nd International Conference on Information Systems Security and Privacy, ICISSP 2016, Rome, Italy, February 19-21, 2016, edited by Olivier Camp et al., SciTePress, 2016, pp. 407–14, doi:10.5220/0005740704070414.*
8. *Roy, Sangita, et al. “Fast and Lean Encrypted Internet Traffic Classification.” Comput. Commun., vol. 186, 2022, pp. 166–73, doi:10.1016/j.comcom.2022.02.003.*

## USTC-TFC2016

- Link: https://github.com/yungshenglu/USTC-TFC2016
- Description: This dataset contains 10 malware families and 10 types of benign
traffic.
    -  The malware classes are:  Cridex (Dridex), Geodo (Emotet), Htbot, Miuref, Neris, Nsis-a, Shifu, Tinba, Virut, Zeus.
    - The benign classes are: BitTorrent, Facetime, FTP, Gmail, MySQL, Outlook, Skype, SMB, Weibo, WorldOfWarcraft.
- Downloadable Size: ~427 MB

### Some Papers That Adopted This Dataset 

1. *Wang, Wei, et al. “Malware Traffic Classification Using Convolutional Neural Network for Representation Learning.” 2017 International Conference on Information Networking, ICOIN 2017, Da Nang, Vietnam, January 11-13, 2017, IEEE, 2017, pp. 712–17, doi:10.1109/ICOIN.2017.7899588.* 
2. *Marı́n, Gonzalo, et al. “DeepMAL - Deep Learning Models for Malware Traffic Detection and Classification.” CoRR, vol. abs/2003.04079, 2020, https://arxiv.org/abs/2003.04079.* 
3. *O. Bader, A. Lichy, C. Hajaj, R. Dubin and A. Dvir, "MalDIST: From Encrypted Traffic Classification to Malware Traffic Detection and Classification," 2022 IEEE 19th Annual Consumer Communications & Networking Conference (CCNC), 2022, pp. 527-533, doi: 10.1109/CCNC49033.2022.9700625.*

## Ariel (BOA2016)

- Link: https://drive.google.com/drive/u/0/folders/0B_43qd7jXKQNMkFTTFVlamhjZ0U?resourcekey=0-G5AifkedFxCa_GPv4sCHtg
- Description: This dataset is from a paper in which the authors collected the data over a period of more than two months, in their lab, using a selenium web crawler for browser traffic. The dataset contains applications’ traffic such as YouTube, and Facebook, which are labeled as browser traffic, and Dropbox and TeamViewer that are labeled as non-browser traffic. The dataset contains more than 20,000 sessions. The average duration of a session was 518 seconds where on average each session had 520 forward packets (the average forward traffic size was 261K bytes) and 637 backward packets (the average backward traffic size was 615K bytes). Almost all of the flows are TLS encrypted.
- Downloadable Size: ~16.3 GB

### Some Papers That Adopted This Dataset 

1. *Rezaei, Shahbaz, and Xin Liu. “How to Achieve High Classification Accuracy with Just a Few Labels: A Semi-Supervised Approach Using Sampled Packets.” CoRR, vol. abs/1812.09761, 2018, http://arxiv.org/abs/1812.09761.* 
2. *Muehlstein, Jonathan, et al. “Analyzing HTTPS Encrypted Traffic to Identify User’s Operating System, Browser and Application.” 14th IEEE Annual Consumer Communications & Networking Conference, CCNC 2017, Las Vegas, NV, USA, January 8-11, 2017, IEEE, 2017, pp. 1–6, doi:10.1109/CCNC.2017.8013420.* 


## malware-traffic-analysis.net (MTA)

- Link: 
- Description: 

### Some Papers That Adopted This Dataset 


## StratosphereIPS Labs Datasets (Starto)

- Link: 
- Description: 

### Some Papers That Adopted This Dataset 
