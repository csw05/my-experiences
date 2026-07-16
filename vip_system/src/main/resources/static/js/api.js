/* ============================================
   VIP会员管理系统 — API 封装层
   ============================================ */

const BASE_URL = 'http://localhost:9999';

// axios 实例
const http = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
});

// 响应拦截器
http.interceptors.response.use(
  response => {
    const body = response.data;
    if (body.code === 2000) {
      return body;
    } else {
      ElMessage.error(body.message || '操作失败');
      return Promise.reject(body);
    }
  },
  error => {
    ElMessage.error('网络异常，请稍后重试');
    return Promise.reject(error);
  }
);

// ==================== 认证模块 ====================

/**
 * 登录：先用用户名查员工获取 userId，再校验密码
 * @param {string} username 用户名
 * @param {string} password 密码
 * @returns {Promise<{userId: number, username: string, name: string}>}
 */
async function login(username, password) {
  // 1. 根据用户名查找员工
  const searchRes = await http.post('/staff/list/search/1/1', { username: username });
  const records = searchRes.data.records;
  if (!records || records.length === 0) {
    ElMessage.error('用户名或密码错误');
    throw new Error('用户不存在');
  }
  const staff = records[0];

  // 2. 校验密码
  await http.post('/user/pwd', { userId: staff.id, password: password });

  return {
    userId: staff.id,
    username: staff.username,
    name: staff.name
  };
}

/**
 * 校验原密码
 * @param {number} userId
 * @param {string} oldPassword
 */
function checkPassword(userId, oldPassword) {
  return http.post('/user/pwd', { userId, password: oldPassword });
}

/**
 * 修改密码
 * @param {number} userId
 * @param {string} newPassword
 */
function updatePassword(userId, newPassword) {
  return http.put('/user/pwd', { userId, password: newPassword });
}

// ==================== 会员管理 ====================

/**
 * 分页条件查询会员
 * @param {number} page
 * @param {number} size
 * @param {object} params — { name, cardNum, payType, birthday }
 */
function getMemberList(page, size, params) {
  return http.post(`/member/list/search/${page}/${size}`, params || {});
}

/** 新增会员 */
function addMember(data) {
  return http.post('/member', data);
}

/** 查询会员详情 */
function getMember(id) {
  return http.get(`/member/${id}`);
}

/** 修改会员 */
function updateMember(id, data) {
  return http.put(`/member/${id}`, data);
}

/** 删除会员 */
function deleteMember(id) {
  return http.delete(`/member/${id}`);
}

// ==================== 商品管理 ====================

/**
 * 分页条件查询商品
 * @param {number} page
 * @param {number} size
 * @param {object} params — { name, code, supplierId }
 */
function getGoodsList(page, size, params) {
  return http.post(`/goods/list/search/${page}/${size}`, params || {});
}

/** 新增商品 */
function addGoods(data) {
  return http.post('/goods', data);
}

/** 查询商品详情 */
function getGoods(id) {
  return http.get(`/goods/${id}`);
}

/** 修改商品 */
function updateGoods(id, data) {
  return http.put(`/goods/${id}`, data);
}

/** 删除商品 */
function deleteGoods(id) {
  return http.delete(`/goods/${id}`);
}

// ==================== 员工管理 ====================

/**
 * 分页条件查询员工
 * @param {number} page
 * @param {number} size
 * @param {object} params — { name, username }
 */
function getStaffList(page, size, params) {
  return http.post(`/staff/list/search/${page}/${size}`, params || {});
}

/** 新增员工 */
function addStaff(data) {
  return http.post('/staff', data);
}

/** 查询员工详情 */
function getStaff(id) {
  return http.get(`/staff/${id}`);
}

/** 修改员工 */
function updateStaff(id, data) {
  return http.put(`/staff/${id}`, data);
}

/** 删除员工 */
function deleteStaff(id) {
  return http.delete(`/staff/${id}`);
}

// ==================== 供应商管理 ====================

/**
 * 分页条件查询供应商
 * @param {number} page
 * @param {number} size
 * @param {object} params — { name, linkman, mobile }
 */
function getSupplierList(page, size, params) {
  return http.post(`/supplier/list/search/${page}/${size}`, params || {});
}

/** 新增供应商 */
function addSupplier(data) {
  return http.post('/supplier', data);
}

/** 查询供应商详情 */
function getSupplier(id) {
  return http.get(`/supplier/${id}`);
}

/** 修改供应商 */
function updateSupplier(id, data) {
  return http.put(`/supplier/${id}`, data);
}

/** 删除供应商 */
function deleteSupplier(id) {
  return http.delete(`/supplier/${id}`);
}

/**
 * 加载全部供应商（用于商品新增/编辑时的下拉选择）
 * 分页拉取一个较大的 size 一次性拿到所有供应商
 */
async function getAllSuppliers() {
  const res = await http.post('/supplier/list/search/1/1000', {});
  return res.data.records || [];
}
