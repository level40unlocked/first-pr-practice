export type PropertyType = 'apartment' | 'house' | 'villa' | 'land';

export interface LocalizedText {
  vi: string;
  ko: string;
  en: string;
}

export interface Property {
  id: string;
  type: PropertyType;
  city: LocalizedText;
  district: LocalizedText;
  title: LocalizedText;
  description: LocalizedText;
  priceUsd: number;
  areaSqm: number;
  bedrooms: number;
  bathrooms: number;
  lat: number;
  lng: number;
  imageColor: string;
  contactName: string;
  contactPhone: string;
}

export const properties: Property[] = [
  {
    id: 'hn-001',
    type: 'apartment',
    city: { vi: 'Hà Nội', ko: '하노이', en: 'Hanoi' },
    district: { vi: 'Quận Cầu Giấy', ko: '꺼우저이 구', en: 'Cau Giay District' },
    title: {
      vi: 'Căn hộ 2 phòng ngủ view hồ tại Cầu Giấy',
      ko: '꺼우저이 호수 전망 침실 2개 아파트',
      en: '2BR Lake-View Apartment in Cau Giay',
    },
    description: {
      vi: 'Căn hộ hiện đại, đầy đủ nội thất, gần trường học và trung tâm thương mại.',
      ko: '풀옵션 가구, 학교와 쇼핑몰 인근에 위치한 모던한 아파트입니다.',
      en: 'Modern fully-furnished apartment near schools and shopping malls.',
    },
    priceUsd: 145000,
    areaSqm: 78,
    bedrooms: 2,
    bathrooms: 2,
    lat: 21.0313,
    lng: 105.7889,
    imageColor: '#f4a261',
    contactName: 'Nguyen Van A',
    contactPhone: '+84 90 123 4567',
  },
  {
    id: 'hn-002',
    type: 'house',
    city: { vi: 'Hà Nội', ko: '하노이', en: 'Hanoi' },
    district: { vi: 'Quận Tây Hồ', ko: '떠이호 구', en: 'Tay Ho District' },
    title: {
      vi: 'Nhà phố 4 tầng gần Hồ Tây',
      ko: '떠이호 인근 4층 타운하우스',
      en: '4-Story Townhouse near West Lake',
    },
    description: {
      vi: 'Nhà mới xây, thiết kế hiện đại, khu vực an ninh yên tĩnh.',
      ko: '신축, 모던한 디자인, 안전하고 조용한 지역입니다.',
      en: 'Newly built, modern design, quiet and secure neighborhood.',
    },
    priceUsd: 620000,
    areaSqm: 180,
    bedrooms: 4,
    bathrooms: 4,
    lat: 21.0583,
    lng: 105.8206,
    imageColor: '#2a9d8f',
    contactName: 'Tran Thi B',
    contactPhone: '+84 91 234 5678',
  },
  {
    id: 'hcmc-001',
    type: 'apartment',
    city: { vi: 'TP. Hồ Chí Minh', ko: '호치민시', en: 'Ho Chi Minh City' },
    district: { vi: 'Quận 2 (Thủ Đức)', ko: '2군 (투득)', en: 'District 2 (Thu Duc)' },
    title: {
      vi: 'Căn hộ cao cấp tại Thảo Điền',
      ko: '타오디엔 고급 아파트',
      en: 'Luxury Apartment in Thao Dien',
    },
    description: {
      vi: 'View sông Sài Gòn, hồ bơi, phòng gym, gần trường quốc tế.',
      ko: '사이공강 전망, 수영장, 헬스장, 국제학교 인근입니다.',
      en: 'Saigon River view, pool, gym, near international schools.',
    },
    priceUsd: 320000,
    areaSqm: 95,
    bedrooms: 3,
    bathrooms: 2,
    lat: 10.8033,
    lng: 106.7378,
    imageColor: '#264653',
    contactName: 'Le Van C',
    contactPhone: '+84 93 345 6789',
  },
  {
    id: 'hcmc-002',
    type: 'villa',
    city: { vi: 'TP. Hồ Chí Minh', ko: '호치민시', en: 'Ho Chi Minh City' },
    district: { vi: 'Quận 7', ko: '7군', en: 'District 7' },
    title: {
      vi: 'Biệt thự sân vườn Phú Mỹ Hưng',
      ko: '푸미흥 정원형 빌라',
      en: 'Garden Villa in Phu My Hung',
    },
    description: {
      vi: 'Biệt thự song lập, sân vườn riêng, khu compound cao cấp.',
      ko: '듀플렉스 빌라, 전용 정원, 프리미엄 컴파운드 단지입니다.',
      en: 'Semi-detached villa with private garden in a premium compound.',
    },
    priceUsd: 980000,
    areaSqm: 260,
    bedrooms: 5,
    bathrooms: 5,
    lat: 10.7291,
    lng: 106.7217,
    imageColor: '#e76f51',
    contactName: 'Pham Thi D',
    contactPhone: '+84 94 456 7890',
  },
  {
    id: 'hcmc-003',
    type: 'apartment',
    city: { vi: 'TP. Hồ Chí Minh', ko: '호치민시', en: 'Ho Chi Minh City' },
    district: { vi: 'Quận 1', ko: '1군', en: 'District 1' },
    title: {
      vi: 'Studio trung tâm Quận 1',
      ko: '1군 중심가 스튜디오',
      en: 'Studio in Downtown District 1',
    },
    description: {
      vi: 'Gần phố đi bộ Nguyễn Huệ, thích hợp cho người độc thân hoặc đầu tư.',
      ko: '응우옌 후에 보행거리 인근, 1인 거주 또는 투자용으로 적합합니다.',
      en: 'Near Nguyen Hue walking street, ideal for singles or investment.',
    },
    priceUsd: 98000,
    areaSqm: 38,
    bedrooms: 1,
    bathrooms: 1,
    lat: 10.7756,
    lng: 106.7019,
    imageColor: '#e9c46a',
    contactName: 'Hoang Van E',
    contactPhone: '+84 95 567 8901',
  },
  {
    id: 'dn-001',
    type: 'apartment',
    city: { vi: 'Đà Nẵng', ko: '다낭', en: 'Da Nang' },
    district: { vi: 'Quận Sơn Trà', ko: '선짜 구', en: 'Son Tra District' },
    title: {
      vi: 'Căn hộ view biển Mỹ Khê',
      ko: '미케 해변 전망 아파트',
      en: 'My Khe Beachfront Apartment',
    },
    description: {
      vi: 'Cách bãi biển Mỹ Khê 200m, ban công hướng biển.',
      ko: '미케 해변에서 200m, 오션뷰 발코니가 있습니다.',
      en: '200m from My Khe Beach, balcony with ocean view.',
    },
    priceUsd: 175000,
    areaSqm: 65,
    bedrooms: 2,
    bathrooms: 2,
    lat: 16.0603,
    lng: 108.2438,
    imageColor: '#457b9d',
    contactName: 'Vo Thi F',
    contactPhone: '+84 96 678 9012',
  },
  {
    id: 'dn-002',
    type: 'land',
    city: { vi: 'Đà Nẵng', ko: '다낭', en: 'Da Nang' },
    district: { vi: 'Quận Ngũ Hành Sơn', ko: '응우한선 구', en: 'Ngu Hanh Son District' },
    title: {
      vi: 'Lô đất nền gần Ngũ Hành Sơn',
      ko: '응우한선 인근 택지',
      en: 'Residential Land Plot near Marble Mountains',
    },
    description: {
      vi: 'Sổ đỏ chính chủ, đường nhựa 6m, phù hợp xây nhà hoặc đầu tư.',
      ko: '소유권 등기 완료, 6m 도로 접함, 주택 건축 또는 투자에 적합합니다.',
      en: 'Clear title, 6m paved road access, suitable for building or investment.',
    },
    priceUsd: 210000,
    areaSqm: 120,
    bedrooms: 0,
    bathrooms: 0,
    lat: 16.0028,
    lng: 108.2637,
    imageColor: '#8d99ae',
    contactName: 'Dang Van G',
    contactPhone: '+84 97 789 0123',
  },
  {
    id: 'nt-001',
    type: 'apartment',
    city: { vi: 'Nha Trang', ko: '나짱', en: 'Nha Trang' },
    district: { vi: 'Trung tâm thành phố', ko: '시내 중심가', en: 'City Center' },
    title: {
      vi: 'Căn hộ nghỉ dưỡng trung tâm Nha Trang',
      ko: '나짱 시내 중심 리조트형 아파트',
      en: 'Resort-Style Apartment in Central Nha Trang',
    },
    description: {
      vi: 'Gần bãi biển Trần Phú, phù hợp cho thuê du lịch.',
      ko: '쩐푸 해변 인근, 관광 임대에 적합합니다.',
      en: 'Near Tran Phu Beach, great for tourist rental income.',
    },
    priceUsd: 132000,
    areaSqm: 55,
    bedrooms: 1,
    bathrooms: 1,
    lat: 12.2451,
    lng: 109.1943,
    imageColor: '#588157',
    contactName: 'Bui Thi H',
    contactPhone: '+84 98 890 1234',
  },
  {
    id: 'hn-003',
    type: 'house',
    city: { vi: 'Hà Nội', ko: '하노이', en: 'Hanoi' },
    district: { vi: 'Quận Hoàng Mai', ko: '호앙마이 구', en: 'Hoang Mai District' },
    title: {
      vi: 'Nhà cấp 4 giá tốt cho gia đình trẻ',
      ko: '신혼부부를 위한 저렴한 단층 주택',
      en: 'Affordable Bungalow for Young Families',
    },
    description: {
      vi: 'Giá hợp lý, gần trường học và chợ dân sinh.',
      ko: '합리적인 가격, 학교와 재래시장 인근에 위치합니다.',
      en: 'Budget-friendly, close to schools and local markets.',
    },
    priceUsd: 89000,
    areaSqm: 60,
    bedrooms: 2,
    bathrooms: 1,
    lat: 20.9764,
    lng: 105.8524,
    imageColor: '#bc6c25',
    contactName: 'Ngo Van I',
    contactPhone: '+84 99 901 2345',
  },
  {
    id: 'hcmc-004',
    type: 'land',
    city: { vi: 'TP. Hồ Chí Minh', ko: '호치민시', en: 'Ho Chi Minh City' },
    district: { vi: 'Quận 9 (Thủ Đức)', ko: '9군 (투득)', en: 'District 9 (Thu Duc)' },
    title: {
      vi: 'Đất nền dự án khu công nghệ cao',
      ko: '하이테크 파크 인근 프로젝트 부지',
      en: 'Land Plot near High-Tech Park',
    },
    description: {
      vi: 'Tiềm năng tăng giá cao, gần khu công nghệ cao TP.HCM.',
      ko: '호치민 하이테크 파크 인근, 높은 시세 상승 잠재력이 있습니다.',
      en: 'High appreciation potential, near HCMC High-Tech Park.',
    },
    priceUsd: 156000,
    areaSqm: 100,
    bedrooms: 0,
    bathrooms: 0,
    lat: 10.8412,
    lng: 106.8098,
    imageColor: '#6d597a',
    contactName: 'Truong Thi K',
    contactPhone: '+84 90 012 3456',
  },
];

export const cities = Array.from(new Set(properties.map((p) => p.city.en)));
export const propertyTypes: PropertyType[] = ['apartment', 'house', 'villa', 'land'];
