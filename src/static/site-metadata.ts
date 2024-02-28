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
  logo: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQTtc69JxHNcmN1ETpMUX4dozAgAN6iPjWalQ&usqp=CAU',
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
