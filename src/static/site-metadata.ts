interface ISiteMetadataResult {
  siteTitle: string;
  siteUrl: string;
  description: string;
  logo: string;
  navLinks: {
    name: string;
    url: string;
  }[];
}

const data: ISiteMetadataResult = {
  siteTitle: '越过大西洋',
  siteUrl: 'https://yihong.run',
  logo: 'https://s11.ax1x.com/2024/02/28/pFwFmMn.jpg',
  description: '越过大西洋',
  navLinks: [
    {
      name: 'Blog',
      url: 'https://github.com/AtlanticF',
    },
    {
      name: 'About',
      url: 'https://github.com/AtlanticF',
    },
  ],
};

export default data;
