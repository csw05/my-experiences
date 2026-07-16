package com.sky.mapper;

import com.sky.entity.User;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import java.util.Map;

@Mapper
public interface UserMapper {
    @Select("<script>select count(id) from user <where><if test='end != null'>and create_time &lt;= #{end}</if><if test='begin != null'>and create_time &gt;= #{begin}</if></where></script>")
    Integer countByMap(Map map);

    @Select("select * from user where id = #{id}")
    User getById(Long id);
}